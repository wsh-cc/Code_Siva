"""Tkinter desktop client for OCHAT."""

from __future__ import annotations

import argparse
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Any

from .api import OchatClient


class OchatApp(tk.Tk):
    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        super().__init__()
        self.title("OCHAT")
        self.geometry("1040x680")
        self.minsize(920, 600)
        self.client = OchatClient(host, port)
        self.user: dict[str, Any] | None = None
        self.friends: list[dict[str, Any]] = []
        self.groups: list[dict[str, Any]] = []
        self.current_target: tuple[str, int] | None = None
        self.messages_by_target: dict[tuple[str, int], list[dict[str, Any]]] = {}
        self._build_styles()
        self._show_login()
        self.after(100, self._poll_events)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_styles(self) -> None:
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TFrame", background="#f5f7fb")
        style.configure("Sidebar.TFrame", background="#ecf1f7")
        style.configure("TLabel", background="#f5f7fb", foreground="#18202c")
        style.configure("Sidebar.TLabel", background="#ecf1f7")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 16, "bold"))
        style.configure("Small.TLabel", font=("Microsoft YaHei UI", 9), foreground="#5b6573")
        style.configure("TButton", padding=(10, 5))
        style.configure("Accent.TButton", padding=(12, 6))
        style.configure("Treeview", rowheight=30, font=("Microsoft YaHei UI", 10))
        style.configure("Treeview.Heading", font=("Microsoft YaHei UI", 10, "bold"))

    def _clear(self) -> None:
        for child in self.winfo_children():
            child.destroy()

    def _show_login(self) -> None:
        self._clear()
        root = ttk.Frame(self, padding=32)
        root.pack(fill=tk.BOTH, expand=True)
        panel = ttk.Frame(root, padding=24)
        panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=420)

        ttk.Label(panel, text="OCHAT", style="Title.TLabel").pack(anchor=tk.W, pady=(0, 4))
        ttk.Label(panel, text="在线互动聊天系统", style="Small.TLabel").pack(anchor=tk.W, pady=(0, 18))

        ttk.Label(panel, text="用户名").pack(anchor=tk.W)
        self.login_username_entry = ttk.Entry(panel)
        self.login_username_entry.pack(fill=tk.X, pady=(4, 12))
        ttk.Label(panel, text="密码").pack(anchor=tk.W)
        self.login_password_entry = ttk.Entry(panel, show="*")
        self.login_password_entry.pack(fill=tk.X, pady=(4, 16))

        actions = ttk.Frame(panel)
        actions.pack(fill=tk.X)
        ttk.Button(actions, text="登录", style="Accent.TButton", command=self._login_from_form).pack(side=tk.LEFT)
        ttk.Button(actions, text="注册新账号", command=self._register_from_form).pack(side=tk.LEFT, padx=8)
        ttk.Button(actions, text="连接设置", command=self._configure_server).pack(side=tk.RIGHT)

        self.login_username_entry.focus_set()
        self.bind("<Return>", lambda _event: self._login_from_form())

    def _configure_server(self) -> None:
        host = simpledialog.askstring("服务器地址", "Host", initialvalue=self.client.host, parent=self)
        if not host:
            return
        port = simpledialog.askinteger("服务器端口", "Port", initialvalue=self.client.port, parent=self, minvalue=1, maxvalue=65535)
        if not port:
            return
        self.client.close()
        self.client = OchatClient(host, port)

    def _login(self, username: str, password: str) -> None:
        self._run_request(
            lambda: self.client.request("login", username=username.strip(), password=password),
            self._on_login_success,
        )

    def _login_from_form(self) -> None:
        username = self.login_username_entry.get().strip()
        password = self.login_password_entry.get()
        if not username or not password:
            messagebox.showinfo("提示", "请输入用户名和密码")
            return
        self._login(username, password)

    def _register_from_form(self) -> None:
        username = self.login_username_entry.get().strip()
        password = self.login_password_entry.get()
        if not username or not password:
            messagebox.showinfo("提示", "请输入用户名和密码")
            return
        self._register_account(username, password)

    def _register_account(self, username: str, password: str) -> None:
        nickname = simpledialog.askstring("昵称", "请输入昵称（可留空）", initialvalue=username.strip(), parent=self) or username.strip()
        self._run_request(
            lambda: self.client.request("register", username=username.strip(), password=password, nickname=nickname),
            lambda _resp: self._login(username, password),
        )

    def _on_login_success(self, response: dict[str, Any]) -> None:
        self.user = response["user"]
        self.friends = response.get("friends", [])
        self.groups = response.get("groups", [])
        self._show_main()

    def _show_main(self) -> None:
        self._clear()
        self.unbind("<Return>")
        root = ttk.Frame(self)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(root, style="Sidebar.TFrame", padding=12)
        sidebar.grid(row=0, column=0, sticky="ns", ipadx=4)
        sidebar.rowconfigure(2, weight=1)

        user_title = self.user["nickname"] if self.user else "OCHAT"
        ttk.Label(sidebar, text=user_title, style="Title.TLabel").grid(row=0, column=0, sticky="ew")
        ttk.Label(sidebar, text="在线", style="Sidebar.TLabel").grid(row=1, column=0, sticky="w", pady=(2, 12))

        self.notebook = ttk.Notebook(sidebar, width=300)
        self.notebook.grid(row=2, column=0, sticky="nsew")

        self.friend_tree = self._build_tree(self.notebook, ("name", "status"), ("联系人", "状态"))
        self.group_tree = self._build_tree(self.notebook, ("name", "role"), ("群聊", "角色"))
        self.notebook.add(self.friend_tree.master, text="好友")
        self.notebook.add(self.group_tree.master, text="群聊")
        self.friend_tree.bind("<<TreeviewSelect>>", self._friend_selected)
        self.group_tree.bind("<<TreeviewSelect>>", self._group_selected)

        friend_actions = ttk.Frame(sidebar, style="Sidebar.TFrame")
        friend_actions.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(friend_actions, text="加好友", command=self._add_friend).pack(side=tk.LEFT)
        ttk.Button(friend_actions, text="改备注", command=self._edit_friend).pack(side=tk.LEFT, padx=6)
        ttk.Button(friend_actions, text="删好友", command=self._remove_friend).pack(side=tk.LEFT)

        group_actions = ttk.Frame(sidebar, style="Sidebar.TFrame")
        group_actions.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(group_actions, text="建群", command=self._create_group).pack(side=tk.LEFT)
        ttk.Button(group_actions, text="邀成员", command=self._invite_member).pack(side=tk.LEFT, padx=6)
        ttk.Button(group_actions, text="成员", command=self._show_members).pack(side=tk.LEFT)

        profile_actions = ttk.Frame(sidebar, style="Sidebar.TFrame")
        profile_actions.grid(row=5, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(profile_actions, text="资料", command=self._edit_profile).pack(side=tk.LEFT)
        ttk.Button(profile_actions, text="搜索消息", command=self._search_messages).pack(side=tk.LEFT, padx=6)
        ttk.Button(profile_actions, text="退出", command=self._logout).pack(side=tk.RIGHT)

        content = ttk.Frame(root, padding=(14, 12))
        content.grid(row=0, column=1, sticky="nsew")
        content.rowconfigure(1, weight=1)
        content.columnconfigure(0, weight=1)

        self.chat_title = ttk.Label(content, text="请选择好友或群聊", style="Title.TLabel")
        self.chat_title.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.chat_text = tk.Text(content, wrap=tk.WORD, state=tk.DISABLED, bg="#ffffff", relief=tk.FLAT, padx=12, pady=12)
        self.chat_text.grid(row=1, column=0, sticky="nsew")
        self.chat_text.tag_configure("mine", foreground="#1b5e20")
        self.chat_text.tag_configure("peer", foreground="#0d47a1")
        self.chat_text.tag_configure("meta", foreground="#6b7280")

        input_bar = ttk.Frame(content)
        input_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        input_bar.columnconfigure(0, weight=1)
        self.message_entry = ttk.Entry(input_bar)
        self.message_entry.grid(row=0, column=0, sticky="ew")
        self.message_entry.bind("<Return>", lambda event: self._send_message())
        ttk.Button(input_bar, text="😊", width=4, command=self._insert_emoji).grid(row=0, column=1, padx=(8, 0))
        ttk.Button(input_bar, text="文件/图片", command=self._send_file).grid(row=0, column=2, padx=(8, 0))
        ttk.Button(input_bar, text="保存文件", command=self._download_latest_file).grid(row=0, column=3, padx=(8, 0))
        ttk.Button(input_bar, text="撤回", command=self._recall_last_message).grid(row=0, column=4, padx=(8, 0))
        ttk.Button(input_bar, text="发送", style="Accent.TButton", command=self._send_message).grid(row=0, column=5, padx=(8, 0))

        self._refresh_friend_tree()
        self._refresh_group_tree()

    def _build_tree(self, parent: ttk.Notebook, columns: tuple[str, ...], headings: tuple[str, ...]) -> ttk.Treeview:
        frame = ttk.Frame(parent)
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=150 if col == "name" else 70, anchor=tk.W)
        tree.pack(fill=tk.BOTH, expand=True)
        return tree

    def _refresh_friend_tree(self) -> None:
        self.friend_tree.delete(*self.friend_tree.get_children())
        for friend in self.friends:
            name = friend.get("remark") or friend.get("nickname") or friend.get("username")
            status = "在线" if friend.get("online") else "离线"
            self.friend_tree.insert("", tk.END, iid=str(friend["id"]), values=(name, status))

    def _refresh_group_tree(self) -> None:
        self.group_tree.delete(*self.group_tree.get_children())
        for group in self.groups:
            self.group_tree.insert("", tk.END, iid=str(group["id"]), values=(group["name"], group.get("my_role", "member")))

    def _friend_selected(self, _event: tk.Event) -> None:
        selected = self.friend_tree.selection()
        if not selected:
            return
        friend_id = int(selected[0])
        friend = next((item for item in self.friends if int(item["id"]) == friend_id), None)
        if not friend:
            return
        self.current_target = ("direct", friend_id)
        self.chat_title.configure(text=f"与 {friend.get('remark') or friend.get('nickname') or friend.get('username')} 私聊")
        self._load_history("messages.direct.history", friend_id=friend_id)

    def _group_selected(self, _event: tk.Event) -> None:
        selected = self.group_tree.selection()
        if not selected:
            return
        group_id = int(selected[0])
        group = next((item for item in self.groups if int(item["id"]) == group_id), None)
        if not group:
            return
        self.current_target = ("group", group_id)
        self.chat_title.configure(text=f"群聊：{group['name']}")
        self._load_history("messages.group.history", group_id=group_id)

    def _load_history(self, action: str, **payload: Any) -> None:
        target = self.current_target
        if not target:
            return
        self._run_request(lambda: self.client.request(action, **payload), lambda resp: self._show_history(target, resp.get("messages", [])))

    def _show_history(self, target: tuple[str, int], messages: list[dict[str, Any]]) -> None:
        self.messages_by_target[target] = self._merge_messages(self.messages_by_target.get(target, []), messages)
        if target == self.current_target:
            self._render_messages(self.messages_by_target[target])

    def _render_messages(self, messages: list[dict[str, Any]]) -> None:
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.delete("1.0", tk.END)
        for message in messages:
            self._append_message(message, render_only=True)
        self.chat_text.configure(state=tk.DISABLED)
        self.chat_text.see(tk.END)

    def _append_message(self, message: dict[str, Any], render_only: bool = False) -> None:
        if self.chat_text["state"] == tk.DISABLED:
            self.chat_text.configure(state=tk.NORMAL)
        mine = self.user and int(message["sender_id"]) == int(self.user["id"])
        tag = "mine" if mine else "peer"
        sender = "我" if mine else message.get("sender_nickname") or message.get("sender_username")
        stamp = message.get("created_at", "")
        status = "（已撤回）" if message.get("status") == "recalled" else ""
        content = message.get("content", "")
        if message.get("message_type") in {"file", "image"} and message.get("file_name"):
            content = f"[{message.get('message_type')}] {message.get('file_name')} 文件ID:{message.get('file_id')} {content}".strip()
        self.chat_text.insert(tk.END, f"{sender} {stamp} {status}\n", tag)
        self.chat_text.insert(tk.END, f"{content}\n\n")
        if not render_only:
            self.chat_text.configure(state=tk.DISABLED)
            self.chat_text.see(tk.END)

    def _send_message(self) -> None:
        if not self.current_target:
            messagebox.showinfo("提示", "请先选择聊天对象")
            return
        content = self.message_entry.get().strip()
        if not content:
            return
        self.message_entry.delete(0, tk.END)
        kind, target_id = self.current_target
        if kind == "direct":
            self._run_request(lambda: self.client.request("messages.direct.send", receiver_id=target_id, content=content), lambda _resp: None)
        else:
            self._run_request(lambda: self.client.request("messages.group.send", group_id=target_id, content=content), lambda _resp: None)

    def _insert_emoji(self) -> None:
        emoji = simpledialog.askstring("表情", "输入表情或选择常用：🙂 😂 👍 🎉 ❤️", initialvalue="🙂", parent=self)
        if emoji:
            self.message_entry.insert(tk.INSERT, emoji)

    def _send_file(self) -> None:
        if not self.current_target:
            messagebox.showinfo("提示", "请先选择聊天对象")
            return
        path = filedialog.askopenfilename(title="选择文件或图片")
        if not path:
            return
        kind, target_id = self.current_target

        def job() -> dict[str, Any]:
            upload = self.client.upload_file(path)
            file_record = upload["file"]
            message_type = "image" if Path(path).suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"} else "file"
            content = f"已发送 {Path(path).name}"
            if kind == "direct":
                return self.client.request(
                    "messages.direct.send",
                    receiver_id=target_id,
                    content=content,
                    message_type=message_type,
                    file_id=file_record["id"],
                )
            return self.client.request(
                "messages.group.send",
                group_id=target_id,
                content=content,
                message_type=message_type,
                file_id=file_record["id"],
            )

        self._run_request(job, lambda _resp: None)

    def _download_latest_file(self) -> None:
        if not self.current_target:
            messagebox.showinfo("提示", "请先选择聊天对象")
            return
        messages = self.messages_by_target.get(self.current_target, [])
        file_messages = [msg for msg in messages if msg.get("file_id")]
        if not file_messages:
            messagebox.showinfo("提示", "当前聊天没有可保存的文件")
            return
        latest = file_messages[-1]
        file_id = int(latest["file_id"])
        filename = latest.get("file_name") or f"ochat_file_{file_id}"
        save_path = filedialog.asksaveasfilename(title="保存文件", initialfile=filename)
        if not save_path:
            return

        def job() -> dict[str, Any]:
            return self.client.download_file(file_id, save_path)

        self._run_request(job, lambda _resp: messagebox.showinfo("保存成功", f"文件已保存到：{save_path}"))

    def _recall_last_message(self) -> None:
        if not self.current_target or not self.user:
            messagebox.showinfo("提示", "请先选择聊天对象")
            return
        messages = self.messages_by_target.get(self.current_target, [])
        mine = [msg for msg in messages if int(msg.get("sender_id", 0)) == int(self.user["id"]) and msg.get("status") != "recalled"]
        if not mine:
            messagebox.showinfo("提示", "当前聊天没有可撤回的自己消息")
            return
        message_id = int(mine[-1]["id"])
        self._run_request(lambda: self.client.request("messages.recall", message_id=message_id), lambda _resp: None)

    def _add_friend(self) -> None:
        username = simpledialog.askstring("添加好友", "请输入对方用户名", parent=self)
        if not username:
            return
        remark = simpledialog.askstring("好友备注", "备注（可留空）", parent=self) or ""
        self._run_request(lambda: self.client.request("friends.add", username=username.strip(), remark=remark), lambda _resp: self._reload_friends())

    def _edit_friend(self) -> None:
        selected = self.friend_tree.selection()
        if not selected:
            return
        friend_id = int(selected[0])
        friend = next((item for item in self.friends if int(item["id"]) == friend_id), None)
        if not friend:
            return
        remark = simpledialog.askstring("修改备注", "备注", initialvalue=friend.get("remark", ""), parent=self) or ""
        group_name = simpledialog.askstring("好友分组", "分组", initialvalue=friend.get("group_name", "Friends"), parent=self) or "Friends"
        self._run_request(
            lambda: self.client.request("friends.update", friend_id=friend_id, remark=remark, group_name=group_name),
            lambda _resp: self._reload_friends(),
        )

    def _remove_friend(self) -> None:
        selected = self.friend_tree.selection()
        if not selected:
            return
        friend_id = int(selected[0])
        if not messagebox.askyesno("删除好友", "确认删除该好友？"):
            return
        self._run_request(lambda: self.client.request("friends.remove", friend_id=friend_id), lambda _resp: self._reload_friends())

    def _create_group(self) -> None:
        name = simpledialog.askstring("创建群聊", "群聊名称", parent=self)
        if not name:
            return
        self._run_request(lambda: self.client.request("groups.create", name=name.strip()), lambda _resp: self._reload_groups())

    def _invite_member(self) -> None:
        if not self.current_target or self.current_target[0] != "group":
            messagebox.showinfo("提示", "请先选择群聊")
            return
        username = simpledialog.askstring("邀请成员", "请输入用户名", parent=self)
        if not username:
            return
        group_id = self.current_target[1]
        self._run_request(lambda: self.client.request("groups.invite", group_id=group_id, username=username.strip()), lambda _resp: self._reload_groups())

    def _show_members(self) -> None:
        if not self.current_target or self.current_target[0] != "group":
            messagebox.showinfo("提示", "请先选择群聊")
            return
        group_id = self.current_target[1]

        def show(response: dict[str, Any]) -> None:
            text = "\n".join(f"{m['username']} ({m['role']})" for m in response.get("members", []))
            messagebox.showinfo("群成员", text or "暂无成员")

        self._run_request(lambda: self.client.request("groups.members", group_id=group_id), show)

    def _edit_profile(self) -> None:
        if not self.user:
            return
        nickname = simpledialog.askstring("个人资料", "昵称", initialvalue=self.user.get("nickname", ""), parent=self)
        if nickname is None:
            return
        signature = simpledialog.askstring("个人资料", "签名", initialvalue=self.user.get("signature", ""), parent=self) or ""
        contact = simpledialog.askstring("个人资料", "联系方式", initialvalue=self.user.get("contact", ""), parent=self) or ""
        avatar = simpledialog.askstring("个人资料", "头像地址", initialvalue=self.user.get("avatar", ""), parent=self) or ""
        self._run_request(
            lambda: self.client.request("profile.update", nickname=nickname, signature=signature, contact=contact, avatar=avatar),
            lambda response: self._profile_updated(response["user"]),
        )

    def _profile_updated(self, user: dict[str, Any]) -> None:
        self.user = user
        self._show_main()

    def _search_messages(self) -> None:
        keyword = simpledialog.askstring("搜索消息", "关键词", parent=self)
        if not keyword:
            return

        def show(response: dict[str, Any]) -> None:
            lines = []
            for msg in response.get("messages", [])[:30]:
                lines.append(f"{msg.get('created_at')} {msg.get('sender_username')}: {msg.get('content')}")
            messagebox.showinfo("搜索结果", "\n".join(lines) or "没有找到消息")

        self._run_request(lambda: self.client.request("messages.search", keyword=keyword.strip()), show)

    def _logout(self) -> None:
        self._run_request(lambda: self.client.request("logout"), lambda _resp: self._show_login())

    def _reload_friends(self) -> None:
        self._run_request(lambda: self.client.request("friends.list"), lambda resp: self._set_friends(resp.get("friends", [])))

    def _reload_groups(self) -> None:
        self._run_request(lambda: self.client.request("groups.list"), lambda resp: self._set_groups(resp.get("groups", [])))

    def _set_friends(self, friends: list[dict[str, Any]]) -> None:
        self.friends = friends
        if hasattr(self, "friend_tree"):
            self._refresh_friend_tree()

    def _set_groups(self, groups: list[dict[str, Any]]) -> None:
        self.groups = groups
        if hasattr(self, "group_tree"):
            self._refresh_group_tree()

    def _handle_event(self, event: dict[str, Any]) -> None:
        action = event.get("action")
        if action == "presence" or action == "friends.updated":
            self._set_friends(event.get("friends", self.friends))
        elif action == "groups.updated":
            self._set_groups(event.get("groups", self.groups))
        elif action == "message.new":
            message = event["message"]
            target = self._target_for_message(message)
            self.messages_by_target[target] = self._merge_messages(self.messages_by_target.get(target, []), [message])
            if target == self.current_target:
                self._render_messages(self.messages_by_target[target])
        elif action == "message.recalled":
            message = event["message"]
            target = self._target_for_message(message)
            messages = self.messages_by_target.get(target, [])
            for index, old in enumerate(messages):
                if old["id"] == message["id"]:
                    messages[index] = message
                    break
            if target == self.current_target:
                self._render_messages(messages)
        elif action == "connection.closed":
            messagebox.showwarning("连接断开", event.get("message", "服务器连接已断开"))

    def _target_for_message(self, message: dict[str, Any]) -> tuple[str, int]:
        if message["conversation_type"] == "group":
            return ("group", int(message["target_id"]))
        assert self.user is not None
        other_id = int(message["target_id"]) if int(message["sender_id"]) == int(self.user["id"]) else int(message["sender_id"])
        return ("direct", other_id)

    @staticmethod
    def _merge_messages(existing: list[dict[str, Any]], incoming: list[dict[str, Any]]) -> list[dict[str, Any]]:
        merged: dict[int, dict[str, Any]] = {}
        for message in [*existing, *incoming]:
            message_id = int(message["id"])
            merged[message_id] = message
        return sorted(merged.values(), key=lambda item: (str(item.get("created_at", "")), int(item["id"])))

    def _poll_events(self) -> None:
        for _ in range(10):
            self.client.poll_event(self._handle_event, timeout=0)
        self.after(100, self._poll_events)

    def _run_request(self, func, on_success) -> None:
        def worker() -> None:
            try:
                response = func()
            except Exception as exc:
                error_message = str(exc)
                self.after(0, lambda error_message=error_message: messagebox.showerror("操作失败", error_message))
                return
            self.after(0, lambda response=response: on_success(response))

        threading.Thread(target=worker, daemon=True).start()

    def _on_close(self) -> None:
        self.client.close()
        self.destroy()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the OCHAT desktop client.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    args = parser.parse_args()
    app = OchatApp(args.host, args.port)
    app.mainloop()


if __name__ == "__main__":
    main()
