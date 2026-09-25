"""Tkinter desktop client for OCHAT."""

from __future__ import annotations

import argparse
import tempfile
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Any, Callable

from .api import OchatClient


EMOJI_CATEGORIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "常用",
        (
            "😊",
            "😂",
            "🤣",
            "😍",
            "😘",
            "😎",
            "😭",
            "😡",
            "👍",
            "👏",
            "🙏",
            "💪",
            "🎉",
            "❤️",
            "🔥",
            "✨",
        ),
    ),
    (
        "表情",
        (
            "😀",
            "😃",
            "😄",
            "😁",
            "😆",
            "😅",
            "🙂",
            "🙃",
            "😉",
            "😌",
            "🤔",
            "🤨",
            "😐",
            "😴",
            "😇",
            "🥳",
            "😢",
            "😤",
            "😱",
            "😬",
            "🤒",
            "🤕",
            "🤯",
            "🥺",
        ),
    ),
    (
        "手势",
        (
            "👋",
            "👌",
            "✌️",
            "🤞",
            "🤟",
            "🤙",
            "👊",
            "✊",
            "🤝",
            "👀",
            "🙌",
            "🫶",
            "👎",
            "☝️",
            "✍️",
            "💅",
        ),
    ),
    (
        "物品",
        (
            "🌹",
            "🍀",
            "🍉",
            "🍔",
            "🍟",
            "🍕",
            "☕",
            "🍵",
            "🎂",
            "🎁",
            "🏆",
            "🎮",
            "📚",
            "💡",
            "📌",
            "🚀",
        ),
    ),
)


class OchatApp(tk.Tk):
    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        super().__init__()
        self.title("OCHAT")
        self.geometry("1320x800")
        self.minsize(1160, 700)
        self.configure(bg="#f4f8fd")

        self.client = OchatClient(host, port)
        self.user: dict[str, Any] | None = None
        self.friends: list[dict[str, Any]] = []
        self.groups: list[dict[str, Any]] = []
        self.conversations: list[dict[str, Any]] = []
        self.requests: dict[str, Any] = {}
        self.current_target: tuple[str, int] | None = None
        self.current_title = "请选择会话"
        self.current_subtitle = "登录后可从左侧选择好友或群聊"
        self.current_avatar_value: Any = ""
        self.chat_window: tk.Toplevel | None = None
        self.chat_windows: dict[tuple[str, int], dict[str, Any]] = {}
        self.view_mode = "chats"
        self.messages_by_target: dict[tuple[str, int], list[dict[str, Any]]] = {}
        self.message_row_widgets: list[tk.Widget] = []
        self.avatar_images: dict[str, tk.PhotoImage] = {}
        self.avatar_loading: set[str] = set()
        self.avatar_failed: set[str] = set()
        self.avatar_waiters: dict[str, list[Callable[[], None]]] = {}
        self.avatar_cache_dir = Path(tempfile.gettempdir()) / "ochat_avatar_cache"
        self.avatar_cache_dir.mkdir(parents=True, exist_ok=True)
        self.inline_images: dict[str, tk.PhotoImage] = {}
        self.inline_image_loading: set[str] = set()
        self.inline_image_failed: set[str] = set()
        self.inline_image_waiters: dict[str, list[Callable[[], None]]] = {}
        self.file_cache_dir = Path(tempfile.gettempdir()) / "ochat_file_cache"
        self.file_cache_dir.mkdir(parents=True, exist_ok=True)

        self._build_styles()
        self._show_login()
        self.after(100, self._poll_events)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_styles(self) -> None:
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TFrame", background="#eef1f5")
        style.configure("Panel.TFrame", background="#ffffff")
        style.configure("TLabel", background="#eef1f5", foreground="#172033", font=("Microsoft YaHei UI", 10))
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 17, "bold"), foreground="#121826")
        style.configure("Small.TLabel", font=("Microsoft YaHei UI", 9), foreground="#657080")
        style.configure("TButton", padding=(10, 6), font=("Microsoft YaHei UI", 9))
        style.configure("Accent.TButton", padding=(14, 7), font=("Microsoft YaHei UI", 10, "bold"))

    def _clear(self) -> None:
        for child in self.winfo_children():
            if isinstance(child, tk.Toplevel):
                continue
            child.destroy()

    def _draw_avatar(
        self,
        canvas: tk.Canvas,
        avatar_value: Any,
        initial: str,
        *,
        size: int,
        bg: str,
        fill: str,
        online: bool = False,
    ) -> None:
        canvas.delete("all")
        canvas.configure(bg=bg)
        key = self._avatar_key(avatar_value)
        image_key = self._avatar_image_key(key, size) if key else ""
        image = self.avatar_images.get(image_key)
        center = size // 2
        inset = 4
        if image:
            canvas.create_image(center, center, image=image)
        else:
            canvas.create_oval(inset, inset, size - inset, size - inset, fill=fill, outline="")
            canvas.create_text(center, center, text=(initial[:1] or "O").upper(), fill="white", font=("Microsoft YaHei UI", max(10, size // 3), "bold"))
            if key and key not in self.avatar_failed:
                self._load_avatar_async(key, size, lambda: self._redraw_avatar_if_alive(canvas, avatar_value, initial, size, bg, fill, online))
        if online:
            canvas.create_oval(size - 14, size - 12, size - 4, size - 2, fill="#22c55e", outline="#ffffff", width=2)

    def _redraw_avatar_if_alive(self, canvas: tk.Canvas, avatar_value: Any, initial: str, size: int, bg: str, fill: str, online: bool) -> None:
        try:
            if canvas.winfo_exists():
                self._draw_avatar(canvas, avatar_value, initial, size=size, bg=bg, fill=fill, online=online)
        except tk.TclError:
            return

    @staticmethod
    def _avatar_key(avatar_value: Any) -> str | None:
        avatar = str(avatar_value or "").strip()
        if not avatar.startswith("file:"):
            return None
        file_id = avatar.split(":", 1)[1]
        return f"file:{int(file_id)}" if file_id.isdigit() else None

    @staticmethod
    def _avatar_image_key(key: str | None, size: int) -> str:
        return f"{key}:{size}" if key else ""

    def _load_avatar_async(self, key: str, size: int, on_loaded: Callable[[], None]) -> None:
        image_key = self._avatar_image_key(key, size)
        if image_key in self.avatar_images:
            on_loaded()
            return
        self.avatar_waiters.setdefault(image_key, []).append(on_loaded)
        if image_key in self.avatar_loading:
            return
        self.avatar_loading.add(image_key)

        def worker() -> None:
            file_id = int(key.split(":", 1)[1])
            target = self.avatar_cache_dir / f"{file_id}.img"
            try:
                if not target.exists():
                    self.client.download_file(file_id, target)
                self.after(0, lambda: self._finish_avatar_load(key, target, size))
            except Exception:
                self.after(0, lambda: self._finish_avatar_load(key, None, size))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_avatar_load(self, key: str, path: Path | None, size: int) -> None:
        image_key = self._avatar_image_key(key, size)
        try:
            if path is not None and path.exists():
                source = tk.PhotoImage(file=str(path))
                self.avatar_images[image_key] = self._make_circular_avatar_image(source, size)
        except tk.TclError:
            self.avatar_failed.add(key)
        if image_key not in self.avatar_images:
            self.avatar_failed.add(key)
        self.avatar_loading.discard(image_key)
        callbacks = self.avatar_waiters.pop(image_key, [])
        for callback in callbacks:
            callback()

    def _make_circular_avatar_image(self, source: tk.PhotoImage, size: int) -> tk.PhotoImage:
        result = tk.PhotoImage(width=size, height=size)
        src_width = source.width()
        src_height = source.height()
        if src_width <= 0 or src_height <= 0:
            return result

        side = min(src_width, src_height)
        left = (src_width - side) // 2
        top = (src_height - side) // 2
        center = (size - 1) / 2
        radius = center
        radius_squared = radius * radius

        for y in range(size):
            source_y = top + min(side - 1, int(y * side / size))
            row: list[str] = []
            row_start: int | None = None
            for x in range(size):
                dx = x - center
                dy = y - center
                inside = dx * dx + dy * dy <= radius_squared
                if not inside:
                    if row_start is not None:
                        result.put("{" + " ".join(row) + "}", to=(row_start, y))
                        row = []
                        row_start = None
                    self._set_photo_pixel_transparent(result, x, y)
                    continue
                if row_start is None:
                    row_start = x
                source_x = left + min(side - 1, int(x * side / size))
                row.append(self._photo_color(source.get(source_x, source_y)))
            if row_start is not None:
                result.put("{" + " ".join(row) + "}", to=(row_start, y))
        return result

    @staticmethod
    def _photo_color(color: Any) -> str:
        if isinstance(color, tuple):
            red, green, blue = color[:3]
            return f"#{int(red):02x}{int(green):02x}{int(blue):02x}"
        return str(color)

    @staticmethod
    def _set_photo_pixel_transparent(image: tk.PhotoImage, x: int, y: int) -> None:
        try:
            image.transparency_set(x, y, True)
        except (AttributeError, tk.TclError):
            pass

    def _show_login(self, username: str = "") -> None:
        self._close_chat_window(clear_target=True)
        self._clear()
        self.geometry("520x460")
        self.minsize(500, 420)
        self.configure(bg="#eef1f5")
        shell = tk.Frame(self, bg="#eef1f5")
        shell.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(shell, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#d9dee8")
        card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=430, height=360)

        tk.Label(card, text="OCHAT", bg="#ffffff", fg="#121826", font=("Microsoft YaHei UI", 24, "bold")).pack(anchor=tk.W, padx=34, pady=(32, 4))
        tk.Label(card, text="更轻、更清楚的在线聊天系统", bg="#ffffff", fg="#657080", font=("Microsoft YaHei UI", 10)).pack(
            anchor=tk.W,
            padx=34,
            pady=(0, 28),
        )

        tk.Label(card, text="用户名", bg="#ffffff", fg="#4b5563").pack(anchor=tk.W, padx=34)
        self.login_username_entry = ttk.Entry(card)
        self.login_username_entry.pack(fill=tk.X, padx=34, pady=(6, 14))
        if username:
            self.login_username_entry.insert(0, username)

        tk.Label(card, text="密码", bg="#ffffff", fg="#4b5563").pack(anchor=tk.W, padx=34)
        self.login_password_entry = ttk.Entry(card, show="*")
        self.login_password_entry.pack(fill=tk.X, padx=34, pady=(6, 20))

        actions = tk.Frame(card, bg="#ffffff")
        actions.pack(fill=tk.X, padx=34)
        ttk.Button(actions, text="登录", style="Accent.TButton", command=self._login_from_form).pack(side=tk.LEFT)
        ttk.Button(actions, text="注册账号", command=self._show_register).pack(side=tk.LEFT, padx=8)
        ttk.Button(actions, text="连接设置", command=self._configure_server).pack(side=tk.RIGHT)

        (self.login_password_entry if username else self.login_username_entry).focus_set()
        self.bind("<Return>", lambda _event: self._login_from_form())

    def _show_register(self) -> None:
        self._clear()
        self.geometry("540x560")
        self.minsize(500, 500)
        shell = tk.Frame(self, bg="#eef1f5")
        shell.pack(fill=tk.BOTH, expand=True)
        card = tk.Frame(shell, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#d9dee8")
        card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=440, height=470)

        tk.Label(card, text="注册 OCHAT", bg="#ffffff", fg="#121826", font=("Microsoft YaHei UI", 22, "bold")).pack(
            anchor=tk.W,
            padx=34,
            pady=(30, 4),
        )
        tk.Label(card, text="创建账号后返回登录页面", bg="#ffffff", fg="#657080").pack(anchor=tk.W, padx=34, pady=(0, 22))

        self.register_username_entry = self._labeled_entry(card, "用户名")
        self.register_nickname_entry = self._labeled_entry(card, "昵称（可留空）")
        self.register_password_entry = self._labeled_entry(card, "密码", show="*")
        self.register_confirm_entry = self._labeled_entry(card, "确认密码", show="*")

        actions = tk.Frame(card, bg="#ffffff")
        actions.pack(fill=tk.X, padx=34, pady=(8, 0))
        ttk.Button(actions, text="注册", style="Accent.TButton", command=self._register_from_form).pack(side=tk.LEFT)
        ttk.Button(actions, text="返回登录", command=lambda: self._show_login(self.register_username_entry.get().strip())).pack(side=tk.LEFT, padx=8)

        self.register_username_entry.focus_set()
        self.bind("<Return>", lambda _event: self._register_from_form())

    def _labeled_entry(self, parent: tk.Widget, label: str, show: str | None = None) -> ttk.Entry:
        tk.Label(parent, text=label, bg="#ffffff", fg="#4b5563").pack(anchor=tk.W, padx=34)
        entry = ttk.Entry(parent, show=show)
        entry.pack(fill=tk.X, padx=34, pady=(6, 14))
        return entry

    def _configure_server(self) -> None:
        host = simpledialog.askstring("服务器地址", "Host", initialvalue=self.client.host, parent=self)
        if not host:
            return
        port = simpledialog.askinteger("服务器端口", "Port", initialvalue=self.client.port, parent=self, minvalue=1, maxvalue=65535)
        if not port:
            return
        self.client.close()
        self.client = OchatClient(host, port)

    def _login_from_form(self) -> None:
        username = self.login_username_entry.get().strip()
        password = self.login_password_entry.get()
        if not username or not password:
            messagebox.showinfo("提示", "请输入用户名和密码")
            return
        self._run_request(lambda: self.client.request("login", username=username, password=password), self._on_login_success)

    def _register_from_form(self) -> None:
        username = self.register_username_entry.get().strip()
        nickname = self.register_nickname_entry.get().strip()
        password = self.register_password_entry.get()
        confirm_password = self.register_confirm_entry.get()
        if not username or not password or not confirm_password:
            messagebox.showinfo("提示", "请输入用户名、密码和确认密码")
            return
        if password != confirm_password:
            messagebox.showinfo("提示", "两次输入的密码不一致，请重新输入")
            self.register_password_entry.delete(0, tk.END)
            self.register_confirm_entry.delete(0, tk.END)
            self.register_password_entry.focus_set()
            return

        def on_success(_response: dict[str, Any]) -> None:
            messagebox.showinfo("注册成功", "账号已创建，请返回登录页面登录")
            self._show_login(username)

        self._run_request(
            lambda: self.client.request("register", username=username, password=password, nickname=nickname or username),
            on_success,
        )

    def _on_login_success(self, response: dict[str, Any]) -> None:
        self.user = response["user"]
        self.friends = response.get("friends", [])
        self.groups = response.get("groups", [])
        self.conversations = response.get("conversations", [])
        self.requests = response.get("requests", {})
        self.current_target = None
        self.current_title = "请选择会话"
        self.current_subtitle = "从左侧会话、好友或群聊开始"
        self.current_avatar_value = ""
        self._show_main()

    def _show_main(self) -> None:
        self._clear()
        self.unbind("<Return>")
        self.geometry("560x760")
        self.minsize(520, 640)
        self.configure(bg="#f4f8fd")

        root = tk.Frame(self, bg="#f4f8fd")
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        self.nav = tk.Frame(root, bg="#0f3154", width=86)
        self.nav.grid(row=0, column=0, sticky="ns")
        self.nav.grid_propagate(False)
        self._build_nav()

        self.list_panel = tk.Frame(root, bg="#fbfdff", width=450, highlightthickness=1, highlightbackground="#dce8f5")
        self.list_panel.grid(row=0, column=1, sticky="nsew")
        self.list_panel.grid_propagate(False)
        self._build_list_panel()

        self._render_list()

    def _build_nav(self) -> None:
        initial = (self.user or {}).get("nickname", "O")[:1].upper()
        avatar = tk.Canvas(self.nav, width=56, height=56, bg="#0f3154", highlightthickness=0)
        avatar.pack(pady=(24, 34))
        self._draw_avatar(avatar, (self.user or {}).get("avatar"), initial, size=54, bg="#0f3154", fill="#2f8cff", online=True)

        self.nav_buttons: dict[str, tk.Button] = {}
        for mode, text in (("chats", "●\n消息"), ("friends", "◇\n联系人"), ("groups", "◎\n群聊"), ("requests", "☆\n申请")):
            btn = tk.Button(
                self.nav,
                text=text,
                bd=0,
                relief=tk.FLAT,
                fg="#d6e5f4",
                activeforeground="#ffffff",
                activebackground="#1e73d8",
                font=("Microsoft YaHei UI", 10, "bold"),
                justify=tk.CENTER,
                command=lambda mode=mode: self._switch_mode(mode),
            )
            btn.pack(fill=tk.X, padx=10, pady=6, ipady=9)
            self.nav_buttons[mode] = btn

        tk.Frame(self.nav, bg="#0f3154").pack(fill=tk.BOTH, expand=True)
        tk.Button(self.nav, text="⚙\n资料", bd=0, fg="#d6e5f4", bg="#0f3154", activebackground="#183d63", command=self._edit_profile).pack(
            fill=tk.X,
            padx=10,
            pady=6,
            ipady=9,
        )
        tk.Button(self.nav, text="☰\n退出", bd=0, fg="#d6e5f4", bg="#0f3154", activebackground="#183d63", command=self._logout).pack(
            fill=tk.X,
            padx=10,
            pady=(6, 22),
            ipady=9,
        )
        self._refresh_nav()

    def _build_list_panel(self) -> None:
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_args: self._render_list())
        header = tk.Frame(self.list_panel, bg="#fbfdff")
        header.pack(fill=tk.X, padx=16, pady=(18, 10))
        search_box = tk.Frame(header, bg="#eef4fb", highlightthickness=1, highlightbackground="#e6eef8")
        search_box.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(search_box, text="⌕", bg="#eef4fb", fg="#8aa0b8", font=("Microsoft YaHei UI", 14)).pack(side=tk.LEFT, padx=(12, 4))
        search = tk.Entry(search_box, textvariable=self.search_var, relief=tk.FLAT, bg="#eef4fb", fg="#111827", insertbackground="#111827")
        search.insert(0, "")
        search.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=9)
        tk.Button(header, text="+", width=3, bd=0, bg="#eef4fb", fg="#1f2937", activebackground="#dbeafe", font=("Microsoft YaHei UI", 18), command=self._primary_add_action).pack(side=tk.RIGHT, padx=(10, 0), ipady=2)

        self.list_title = tk.Label(self.list_panel, bg="#fbfdff", fg="#121826", font=("Microsoft YaHei UI", 1))
        self.list_title.pack_forget()

        self.list_canvas = tk.Canvas(self.list_panel, bg="#fbfdff", bd=0, highlightthickness=0)
        self.list_canvas.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self.list_content = tk.Frame(self.list_canvas, bg="#fbfdff")
        self.list_window = self.list_canvas.create_window((0, 0), window=self.list_content, anchor=tk.NW, width=358)
        self.list_content.bind("<Configure>", lambda _event: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all")))
        self.list_canvas.bind("<Configure>", lambda event: self.list_canvas.itemconfigure(self.list_window, width=event.width))
        self._bind_canvas_mousewheel(self.list_canvas)
        self.list_actions = tk.Frame(self.list_panel, bg="#fbfdff", height=52)
        self.list_actions.pack(fill=tk.X, padx=12, pady=(6, 12))

    def _chat_window_exists(self, target: tuple[str, int] | None = None) -> bool:
        if target is not None:
            view = self.chat_windows.get(target)
            if not view:
                return False
            try:
                return bool(view["window"].winfo_exists())
            except tk.TclError:
                return False
        try:
            return self.chat_window is not None and self.chat_window.winfo_exists()
        except tk.TclError:
            return False

    def _activate_chat_window(self, target: tuple[str, int]) -> dict[str, Any] | None:
        view = self.chat_windows.get(target)
        if not view or not self._chat_window_exists(target):
            return None
        self.current_target = target
        self.current_title = str(view.get("title", ""))
        self.current_subtitle = str(view.get("subtitle", ""))
        self.current_avatar_value = view.get("avatar_value", "")
        self.chat_window = view["window"]
        self.chat_panel = view["panel"]
        self.header = view["header"]
        self.chat_avatar_canvas = view["chat_avatar_canvas"]
        self.chat_title_label = view["chat_title_label"]
        self.chat_subtitle_label = view["chat_subtitle_label"]
        self.header_actions = view["header_actions"]
        self.message_canvas = view["message_canvas"]
        self.message_scrollbar = view["message_scrollbar"]
        self.message_content = view["message_content"]
        self.message_window = view["message_window"]
        self.input_text = view["input_text"]
        self.message_row_widgets = view["message_row_widgets"]
        return view

    def _restore_chat_selection(
        self,
        target: tuple[str, int] | None,
        title: str,
        subtitle: str,
        avatar_value: Any,
    ) -> None:
        self.current_target = target
        self.current_title = title
        self.current_subtitle = subtitle
        self.current_avatar_value = avatar_value
        if target and target in self.chat_windows:
            self._activate_chat_window(target)

    def _ensure_chat_window(self, target: tuple[str, int]) -> None:
        if self._chat_window_exists(target):
            title = self.current_title
            subtitle = self.current_subtitle
            avatar_value = self.current_avatar_value
            view = self._activate_chat_window(target)
            if view is not None:
                view["title"] = title
                view["subtitle"] = subtitle
                view["avatar_value"] = avatar_value
                self.current_title = title
                self.current_subtitle = subtitle
                self.current_avatar_value = avatar_value
                view["window"].lift()
            return

        window = tk.Toplevel(self)
        self.chat_window = window
        window.title("OCHAT - 聊天")
        window.geometry("980x720")
        window.minsize(760, 520)
        window.configure(bg="#f1f7ff")
        window.protocol("WM_DELETE_WINDOW", lambda target=target: self._close_chat_window(target))

        self.chat_panel = tk.Frame(window, bg="#f1f7ff")
        self.chat_panel.pack(fill=tk.BOTH, expand=True)
        self.chat_panel.columnconfigure(0, weight=1)
        self.chat_panel.rowconfigure(1, weight=1)
        self.message_row_widgets = []
        self._build_chat_panel(target)
        self.chat_windows[target] = {
            "window": window,
            "panel": self.chat_panel,
            "header": self.header,
            "chat_avatar_canvas": self.chat_avatar_canvas,
            "chat_title_label": self.chat_title_label,
            "chat_subtitle_label": self.chat_subtitle_label,
            "header_actions": self.header_actions,
            "message_canvas": self.message_canvas,
            "message_scrollbar": self.message_scrollbar,
            "message_content": self.message_content,
            "message_window": self.message_window,
            "input_text": self.input_text,
            "message_row_widgets": self.message_row_widgets,
            "title": self.current_title,
            "subtitle": self.current_subtitle,
            "avatar_value": self.current_avatar_value,
        }

    def _close_chat_window(self, target: tuple[str, int] | None = None, clear_target: bool = True) -> None:
        if hasattr(self, "emoji_window"):
            try:
                if self.emoji_window.winfo_exists():
                    self.emoji_window.destroy()
            except tk.TclError:
                pass
        targets = list(self.chat_windows) if target is None else [target]
        for item in targets:
            view = self.chat_windows.pop(item, None)
            if not view:
                continue
            try:
                if view["window"].winfo_exists():
                    view["window"].destroy()
            except tk.TclError:
                pass
        if target is None or self.current_target == target:
            self.chat_window = None
            self.message_row_widgets = []
        if clear_target and (target is None or self.current_target == target):
            self.current_target = None
            self.current_title = "请选择会话"
            self.current_subtitle = "从左侧会话、好友或群聊开始"
            self.current_avatar_value = ""
            if hasattr(self, "list_content"):
                self._render_list()
        elif clear_target and hasattr(self, "list_content"):
            self._render_list()

    def _build_chat_panel(self, target: tuple[str, int]) -> None:
        self.header = tk.Frame(self.chat_panel, bg="#ffffff", height=78, highlightthickness=1, highlightbackground="#dce8f5")
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        title_area = tk.Frame(self.header, bg="#ffffff")
        title_area.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=22, pady=12)
        self.chat_avatar_canvas = tk.Canvas(title_area, width=52, height=52, bg="#ffffff", highlightthickness=0)
        self.chat_avatar_canvas.pack(side=tk.LEFT, padx=(0, 12))
        if target[0] == "direct":
            self._bind_click(self.chat_avatar_canvas, lambda target=target: self._show_direct_profile(target))
        title_text = tk.Frame(title_area, bg="#ffffff")
        title_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.chat_title_label = tk.Label(title_text, bg="#ffffff", fg="#0f172a", font=("Microsoft YaHei UI", 17, "bold"), anchor=tk.W)
        self.chat_title_label.pack(anchor=tk.W)
        self.chat_subtitle_label = tk.Label(title_text, bg="#ffffff", fg="#64748b", font=("Microsoft YaHei UI", 9), anchor=tk.W)
        self.chat_subtitle_label.pack(anchor=tk.W, pady=(4, 0))

        self.header_actions = tk.Frame(self.header, bg="#ffffff")
        self.header_actions.pack(side=tk.RIGHT, padx=(0, 16))

        message_area = tk.Frame(self.chat_panel, bg="#f1f7ff")
        message_area.grid(row=1, column=0, sticky="nsew")
        message_area.rowconfigure(0, weight=1)
        message_area.columnconfigure(0, weight=1)

        self.message_canvas = tk.Canvas(message_area, bg="#f1f7ff", bd=0, highlightthickness=0)
        self.message_scrollbar = ttk.Scrollbar(message_area, orient=tk.VERTICAL, command=self.message_canvas.yview)
        self.message_canvas.configure(yscrollcommand=self.message_scrollbar.set)
        self.message_canvas.grid(row=0, column=0, sticky="nsew")
        self.message_scrollbar.grid(row=0, column=1, sticky="ns")
        self.message_content = tk.Frame(self.message_canvas, bg="#f1f7ff")
        self.message_window = self.message_canvas.create_window((0, 0), window=self.message_content, anchor=tk.NW)
        self.message_content.bind("<Configure>", lambda _event: self.message_canvas.configure(scrollregion=self.message_canvas.bbox("all")))
        self.message_canvas.bind("<Configure>", lambda event, target=target: (self._activate_chat_window(target), self.message_canvas.itemconfigure(self.message_window, width=event.width), self._resize_message_rows(target)))
        self._bind_canvas_mousewheel(self.message_canvas)

        composer = tk.Frame(self.chat_panel, bg="#ffffff", height=112, highlightthickness=1, highlightbackground="#dce8f5")
        composer.grid(row=2, column=0, sticky="ew")
        composer.grid_propagate(False)

        toolbar = tk.Frame(composer, bg="#ffffff")
        toolbar.pack(fill=tk.X, padx=22, pady=(10, 4))
        for text, command in (
            ("表情", lambda target=target: self._insert_emoji(target)),
            ("图片/文件", lambda target=target: self._send_file(target)),
            ("下载文件", lambda target=target: self._download_latest_file(target)),
            ("撤回", lambda target=target: self._recall_last_message(target)),
            ("搜索", self._search_messages),
        ):
            tk.Button(toolbar, text=text, bd=0, bg="#ffffff", fg="#34495e", activebackground="#eef4fb", font=("Microsoft YaHei UI", 10), command=command).pack(side=tk.LEFT, padx=(0, 18), ipadx=4, ipady=2)

        entry_row = tk.Frame(composer, bg="#ffffff")
        entry_row.pack(fill=tk.BOTH, expand=True, padx=22, pady=(0, 14))
        entry_row.columnconfigure(0, weight=1)
        self.input_text = tk.Text(entry_row, height=2, wrap=tk.WORD, relief=tk.FLAT, bg="#f8fbff", padx=14, pady=10, font=("Microsoft YaHei UI", 10), highlightthickness=1, highlightbackground="#dbe7f5")
        self.input_text.grid(row=0, column=0, sticky="nsew")
        self.input_text.bind("<Return>", lambda event, target=target: self._send_from_text(event, target))
        tk.Button(entry_row, text="发送", bd=0, bg="#1683ff", fg="#ffffff", activebackground="#0f6fd8", font=("Microsoft YaHei UI", 11, "bold"), command=lambda target=target: self._send_message(target)).grid(row=0, column=1, padx=(12, 0), ipadx=22, sticky="nsew")

    def _switch_mode(self, mode: str) -> None:
        self.view_mode = mode
        self._refresh_nav()
        self._render_list()

    def _refresh_nav(self) -> None:
        for mode, button in getattr(self, "nav_buttons", {}).items():
            active = mode == self.view_mode
            if mode == "requests":
                count = int(self.requests.get("incoming_count") or 0)
                button.configure(text=f"☆\n申请({count})" if count else "☆\n申请")
            button.configure(bg="#1683ff" if active else "#0f3154", fg="#ffffff" if active else "#d6e5f4")

    def _primary_add_action(self) -> None:
        if self.view_mode == "groups":
            self._create_group()
        elif self.view_mode == "requests":
            self._reload_requests()
        else:
            self._add_friend()

    def _render_list(self) -> None:
        if not hasattr(self, "list_content"):
            return
        for child in self.list_content.winfo_children():
            child.destroy()
        titles = {"chats": "消息", "friends": "好友", "groups": "群聊", "requests": "申请"}
        self.list_title.configure(text=titles[self.view_mode])
        self._render_list_actions()
        keyword = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""

        if self.view_mode == "chats":
            rows = [item for item in self.conversations if self._matches(item, keyword, ("title", "preview", "subtitle"))]
            for conversation in rows:
                self._add_list_row(
                    title=str(conversation.get("title", "")),
                    subtitle=str(conversation.get("preview", "暂无消息")),
                    meta=str(conversation.get("subtitle", "")),
                    avatar_value=conversation.get("peer", {}).get("avatar") if conversation.get("conversation_type") == "direct" else "",
                    unread=int(conversation.get("unread_count") or 0),
                    online=bool(conversation.get("online")),
                    selected=self.current_target == (conversation["conversation_type"], int(conversation["target_id"])),
                    command=lambda conversation=conversation: self._open_conversation(conversation),
                )
        elif self.view_mode == "friends":
            rows = [item for item in self.friends if self._matches(item, keyword, ("username", "nickname", "remark", "group_name"))]
            for friend in rows:
                name = friend.get("remark") or friend.get("nickname") or friend.get("username")
                subtitle = f"{friend.get('group_name', 'Friends')} · {friend.get('signature') or friend.get('username')}"
                self._add_list_row(
                    title=str(name),
                    subtitle=str(subtitle),
                    meta="在线" if friend.get("online") else "离线",
                    avatar_value=friend.get("avatar", ""),
                    unread=int(friend.get("unread_count") or 0),
                    online=bool(friend.get("online")),
                    selected=self.current_target == ("direct", int(friend["id"])),
                    command=lambda friend=friend: self._open_direct(friend),
                )
        elif self.view_mode == "groups":
            rows = [item for item in self.groups if self._matches(item, keyword, ("name", "group_remark", "my_role"))]
            for group in rows:
                title = group.get("group_remark") or group.get("name", "")
                subtitle = self._group_chat_subtitle(group)
                self._add_list_row(
                    title=str(title),
                    subtitle=subtitle,
                    meta="群聊",
                    avatar_value="",
                    unread=int(group.get("unread_count") or 0),
                    online=False,
                    selected=self.current_target == ("group", int(group["id"])),
                    command=lambda group=group: self._open_group(group),
                )
        else:
            rows = self._request_rows()
            if keyword:
                rows = [row for row in rows if keyword in row["title"].lower() or keyword in row["subtitle"].lower()]
            for row in rows:
                self._add_list_row(
                    title=row["title"],
                    subtitle=row["subtitle"],
                    meta=row["meta"],
                    avatar_value="",
                    unread=1 if row["direction"] == "incoming" else 0,
                    online=False,
                    selected=False,
                    command=row["command"],
                )
        if not self.list_content.winfo_children():
            tk.Label(self.list_content, text="没有匹配内容", bg="#fbfdff", fg="#7b8794", pady=28).pack(fill=tk.X)

    def _render_list_actions(self) -> None:
        for child in self.list_actions.winfo_children():
            child.destroy()
        actions: list[tuple[str, Callable[[], None]]] = [("刷新", self._reload_all_lists)]
        if self.view_mode == "chats":
            actions.append(("加好友", self._add_friend))
            actions.append(("建群", self._create_group))
        elif self.view_mode == "friends":
            actions.append(("加好友", self._add_friend))
            actions.append(("改备注", self._edit_friend))
            actions.append(("删除", self._remove_friend))
        else:
            if self.view_mode == "groups":
                actions.append(("建群", self._create_group))
                actions.append(("邀请", self._invite_member))
                actions.append(("群面板", self._show_members))
            else:
                actions.append(("加好友", self._add_friend))
                actions.append(("刷新申请", self._reload_requests))
        for text, command in actions:
            tk.Button(
                self.list_actions,
                text=text,
                bd=0,
                bg="#eef4fb",
                fg="#34495e",
                activebackground="#dbeafe",
                command=command,
            ).pack(side=tk.LEFT, padx=4, ipadx=5, ipady=5)

    @staticmethod
    def _matches(item: dict[str, Any], keyword: str, fields: tuple[str, ...]) -> bool:
        if not keyword:
            return True
        return any(keyword in str(item.get(field, "")).lower() for field in fields)

    def _request_rows(self) -> list[dict[str, Any]]:
        friend_requests = self.requests.get("friend_requests", {})
        group_invitations = self.requests.get("group_invitations", {})
        rows: list[dict[str, Any]] = []
        for item in friend_requests.get("incoming", []):
            name = item.get("requester_nickname") or item.get("requester_username")
            rows.append(
                {
                    "title": f"好友申请：{name}",
                    "subtitle": item.get("message") or f"{item.get('requester_username')} 想添加你为好友",
                    "meta": "待处理",
                    "direction": "incoming",
                    "command": lambda item=item: self._respond_friend_request(item),
                }
            )
        for item in friend_requests.get("outgoing", []):
            name = item.get("receiver_nickname") or item.get("receiver_username")
            rows.append(
                {
                    "title": f"已发送好友申请：{name}",
                    "subtitle": item.get("message") or "等待对方处理",
                    "meta": "等待",
                    "direction": "outgoing",
                    "command": lambda: None,
                }
            )
        for item in group_invitations.get("incoming", []):
            rows.append(
                {
                    "title": f"群邀请：{item.get('group_name')}",
                    "subtitle": item.get("message") or f"{item.get('inviter_username')} 邀请你加入群聊",
                    "meta": "待处理",
                    "direction": "incoming",
                    "command": lambda item=item: self._respond_group_invitation(item),
                }
            )
        for item in group_invitations.get("outgoing", []):
            rows.append(
                {
                    "title": f"已发送群邀请：{item.get('group_name')}",
                    "subtitle": f"等待 {item.get('receiver_username')} 处理",
                    "meta": "等待",
                    "direction": "outgoing",
                    "command": lambda: None,
                }
            )
        return rows

    def _add_list_row(
        self,
        *,
        title: str,
        subtitle: str,
        meta: str,
        avatar_value: Any = "",
        unread: int,
        online: bool,
        selected: bool,
        command: Callable[[], None],
    ) -> None:
        bg = "#eaf3ff" if selected else "#fbfdff"
        hover = "#f0f6ff"
        row = tk.Frame(self.list_content, bg=bg, height=76)
        row.pack(fill=tk.X, padx=10, pady=2)
        row.pack_propagate(False)

        avatar_canvas = tk.Canvas(row, width=46, height=54, bg=bg, highlightthickness=0)
        avatar_canvas.pack(side=tk.LEFT, padx=(10, 8), pady=10)
        self._draw_avatar(avatar_canvas, avatar_value, title, size=48, bg=bg, fill="#8bb7f0" if not selected else "#5ea8ff", online=online)

        text_box = tk.Frame(row, bg=bg)
        text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        top = tk.Frame(text_box, bg=bg)
        top.pack(fill=tk.X)
        tk.Label(top, text=title, bg=bg, fg="#0f172a", font=("Microsoft YaHei UI", 10, "bold"), anchor=tk.W).pack(side=tk.LEFT)
        tk.Label(top, text=meta, bg=bg, fg="#94a3b8", font=("Microsoft YaHei UI", 8), anchor=tk.E).pack(side=tk.RIGHT, padx=(6, 10))
        tk.Label(text_box, text=subtitle, bg=bg, fg="#64748b", font=("Microsoft YaHei UI", 9), anchor=tk.W).pack(fill=tk.X, pady=(7, 0))

        if unread > 0:
            badge = tk.Label(row, text=str(min(unread, 99)), bg="#ff4d4f", fg="#ffffff", font=("Microsoft YaHei UI", 8, "bold"), width=3)
            badge.pack(side=tk.RIGHT, padx=(0, 10))

        self._bind_click(row, command)
        row.bind("<Enter>", lambda _event, row=row: row.configure(bg=hover if not selected else bg))
        row.bind("<Leave>", lambda _event, row=row: row.configure(bg=bg))

    def _bind_click(self, widget: tk.Widget, command: Callable[[], None]) -> None:
        widget.bind("<Button-1>", lambda _event: command())
        widget.configure(cursor="hand2")
        for child in widget.winfo_children():
            self._bind_click(child, command)

    @staticmethod
    def _bind_canvas_mousewheel(canvas: tk.Canvas) -> None:
        def on_mousewheel(event: tk.Event) -> str:
            canvas.yview_scroll(-1 * int(event.delta / 120), "units")
            return "break"

        canvas.bind("<Enter>", lambda _event: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda _event: canvas.unbind_all("<MouseWheel>"))

    def _open_conversation(self, conversation: dict[str, Any]) -> None:
        kind = str(conversation["conversation_type"])
        target_id = int(conversation["target_id"])
        self.current_title = str(conversation.get("title", ""))
        self.current_subtitle = str(conversation.get("subtitle", ""))
        if kind == "direct":
            self.current_avatar_value = conversation.get("peer", {}).get("avatar", "")
        else:
            self.current_avatar_value = conversation.get("group", {}).get("avatar", "")
        self.current_target = (kind, target_id)
        target = self.current_target
        self._ensure_chat_window(target)
        self._render_chat_header(target)
        self._render_messages(self.messages_by_target.get(target, []), target)
        if kind == "direct":
            self._load_history("messages.direct.history", friend_id=target_id)
        else:
            self._load_history("messages.group.history", group_id=target_id)
        self._render_list()

    def _open_direct(self, friend: dict[str, Any]) -> None:
        name = friend.get("remark") or friend.get("nickname") or friend.get("username")
        self._open_conversation(
            {
                "conversation_type": "direct",
                "target_id": friend["id"],
                "title": name,
                "subtitle": "在线" if friend.get("online") else "离线",
                "peer": friend,
            }
        )

    def _open_group(self, group: dict[str, Any]) -> None:
        title = group.get("group_remark") or group["name"]
        subtitle = self._group_chat_subtitle(group)
        self._open_conversation(
            {
                "conversation_type": "group",
                "target_id": group["id"],
                "title": title,
                "subtitle": subtitle,
                "group": group,
            }
        )

    def _render_chat_header(self, target: tuple[str, int] | None = None) -> None:
        if target is not None:
            self._activate_chat_window(target)
        if self._chat_window_exists(self.current_target) and hasattr(self, "chat_title_label"):
            assert self.chat_window is not None
            if self.current_target in self.chat_windows:
                view = self.chat_windows[self.current_target]
                view["title"] = self.current_title
                view["subtitle"] = self.current_subtitle
                view["avatar_value"] = self.current_avatar_value
            self.chat_window.title(f"OCHAT - {self.current_title}")
            self.chat_title_label.configure(text=self.current_title)
            self.chat_subtitle_label.configure(text=self.current_subtitle)
            avatar_value = self.current_avatar_value
            initial = self.current_title or "O"
            self._draw_avatar(self.chat_avatar_canvas, avatar_value, initial, size=50, bg="#ffffff", fill="#60a5fa")
            self._render_chat_header_actions(self.current_target)

    def _render_chat_header_actions(self, target: tuple[str, int] | None = None) -> None:
        if target is not None:
            self._activate_chat_window(target)
        if not hasattr(self, "header_actions"):
            return
        for child in self.header_actions.winfo_children():
            child.destroy()
        if not self.current_target:
            return
        actions: list[tuple[str, Callable[[], None]]] = []
        if self.current_target[0] == "direct":
            actions.append(("搜索消息", self._search_messages))
        if self.current_target[0] == "group":
            group_target = self.current_target
            actions.append(("群面板", lambda target=group_target: self._show_members(target)))
        for text, command in actions:
            tk.Button(
                self.header_actions,
                text=text,
                bd=0,
                bg="#ffffff",
                fg="#34495e",
                activebackground="#eef4fb",
                font=("Microsoft YaHei UI", 10),
                command=command,
            ).pack(side=tk.LEFT, padx=8, ipadx=6, ipady=5)

    def _group_chat_subtitle(self, group: dict[str, Any]) -> str:
        parts: list[str] = []
        if group.get("group_remark"):
            parts.append(f"群名：{group.get('name', '')}")
        parts.append(f"群身份：{self._group_role_label(str(group.get('my_role', 'member')))}")
        if group.get("my_alias"):
            parts.append(f"我的群昵称：{group.get('my_alias')}")
        return " · ".join(parts)

    def _profile_for_user_id(self, user_id: int) -> dict[str, Any] | None:
        if self.user and int(self.user.get("id", 0)) == int(user_id):
            return self.user
        return next((friend for friend in self.friends if int(friend["id"]) == int(user_id)), None)

    def _show_direct_profile(self, target: tuple[str, int]) -> None:
        if target[0] != "direct":
            return
        profile = self._profile_for_user_id(target[1])
        if not profile:
            messagebox.showinfo("提示", "没有找到对方资料")
            return
        self._show_user_profile(profile, title="好友资料")

    def _show_message_sender_profile(self, message: dict[str, Any], target: tuple[str, int] | None) -> None:
        if not self.user:
            return
        sender_id = int(message.get("sender_id", 0))
        if sender_id == int(self.user["id"]):
            return
        profile = self._profile_for_user_id(sender_id) or {
            "id": sender_id,
            "username": message.get("sender_username", ""),
            "nickname": message.get("sender_group_alias") or message.get("sender_nickname", ""),
            "avatar": message.get("sender_avatar", ""),
        }
        self._show_user_profile(profile, title="个人资料")

    def _show_user_profile(self, profile: dict[str, Any], *, title: str = "个人资料", parent: tk.Widget | None = None) -> None:
        window = tk.Toplevel(parent or self)
        window.title(title)
        window.geometry("420x520")
        window.minsize(380, 460)
        window.configure(bg="#ffffff")
        window.transient(parent or self)

        header = tk.Frame(window, bg="#ffffff")
        header.pack(fill=tk.X, padx=24, pady=(22, 14))
        avatar = tk.Canvas(header, width=72, height=72, bg="#ffffff", highlightthickness=0)
        avatar.pack(side=tk.LEFT, padx=(0, 16))
        name = str(profile.get("alias") or profile.get("remark") or profile.get("nickname") or profile.get("username") or "用户")
        self._draw_avatar(avatar, profile.get("avatar", ""), name, size=72, bg="#ffffff", fill="#60a5fa")
        title_box = tk.Frame(header, bg="#ffffff")
        title_box.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(title_box, text=name, bg="#ffffff", fg="#111827", font=("Microsoft YaHei UI", 17, "bold"), anchor=tk.W).pack(anchor=tk.W)
        tk.Label(title_box, text=f"用户名：{profile.get('username', '')}", bg="#ffffff", fg="#64748b", anchor=tk.W).pack(anchor=tk.W, pady=(6, 0))

        body = tk.Frame(window, bg="#ffffff")
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 18))
        body.columnconfigure(1, weight=1)

        def add_row(row: int, label: str, value: Any) -> None:
            text = "" if value is None else str(value).strip()
            tk.Label(body, text=label, bg="#ffffff", fg="#64748b", anchor=tk.W).grid(row=row, column=0, sticky="nw", pady=7)
            tk.Label(body, text=text or "未填写", bg="#ffffff", fg="#111827", anchor=tk.W, justify=tk.LEFT, wraplength=260).grid(
                row=row,
                column=1,
                sticky="ew",
                padx=(18, 0),
                pady=7,
            )

        rows: list[tuple[str, Any]] = [
            ("昵称", profile.get("nickname", "")),
            ("群昵称", profile.get("alias", "")),
            ("签名", profile.get("signature", "")),
            ("联系方式", profile.get("contact", "")),
            ("性别", profile.get("gender", "")),
            ("生日", profile.get("birthday", "")),
            ("年龄", profile.get("age", "")),
            ("住址", profile.get("address", "")),
        ]
        for index, (label, value) in enumerate(rows):
            add_row(index, label, value)

        actions = tk.Frame(window, bg="#ffffff")
        actions.pack(fill=tk.X, padx=24, pady=(0, 22))
        ttk.Button(actions, text="关闭", command=window.destroy).pack(side=tk.RIGHT)

    def _current_group(self, target: tuple[str, int] | None = None) -> dict[str, Any] | None:
        target = target or self.current_target
        if not target or target[0] != "group":
            return None
        group_id = target[1]
        return next((group for group in self.groups if int(group["id"]) == group_id), None)

    def _update_current_group_alias(self, target: tuple[str, int] | None = None) -> None:
        group = self._current_group(target)
        if not group or not self.user:
            messagebox.showinfo("提示", "请先选择群聊")
            return
        group_id = int(group["id"])
        member_id = int(self.user["id"])
        current_alias = str(group.get("my_alias") or "")
        alias = simpledialog.askstring("修改我的群昵称", "我在这个群里的昵称", initialvalue=current_alias, parent=self)
        if alias is None:
            return
        self._run_request(
            lambda: self.client.request("groups.member_alias.update", group_id=group_id, member_id=member_id, alias=alias.strip()),
            lambda _resp: self._reload_all_lists(),
        )

    def _render_empty_chat(self, target: tuple[str, int] | None = None) -> None:
        if target is not None:
            self._activate_chat_window(target)
        if not self._chat_window_exists(self.current_target) or not hasattr(self, "message_content"):
            return
        self._destroy_message_rows(self.current_target)
        label = tk.Label(
            self.message_content,
            text="请选择一个会话开始聊天",
            bg="#f1f7ff",
            fg="#8aa0b8",
            font=("Microsoft YaHei UI", 12),
        )
        label.pack(pady=120)
        self.message_row_widgets.append(label)
        self._scroll_messages_to_latest(self.current_target)

    def _load_history(self, action: str, **payload: Any) -> None:
        target = self.current_target
        if not target:
            return
        self._run_request(lambda: self.client.request(action, **payload), lambda resp: self._show_history(target, resp.get("messages", [])))

    def _show_history(self, target: tuple[str, int], messages: list[dict[str, Any]]) -> None:
        self.messages_by_target[target] = self._merge_messages(self.messages_by_target.get(target, []), messages)
        if self._chat_window_exists(target):
            previous_target = self.current_target
            previous_title = self.current_title
            previous_subtitle = self.current_subtitle
            previous_avatar = self.current_avatar_value
            self._render_messages(self.messages_by_target[target], target)
            if previous_target != target:
                self._restore_chat_selection(previous_target, previous_title, previous_subtitle, previous_avatar)
        self._reload_conversations()

    def _render_messages(self, messages: list[dict[str, Any]], target: tuple[str, int] | None = None) -> None:
        if target is not None:
            self._activate_chat_window(target)
        if not self._chat_window_exists(self.current_target) or not hasattr(self, "message_content"):
            return
        self._destroy_message_rows(self.current_target)
        if not messages:
            label = tk.Label(
                self.message_content,
                text="暂无消息",
                bg="#f1f7ff",
                fg="#8aa0b8",
                font=("Microsoft YaHei UI", 12),
            )
            label.pack(pady=120)
            self.message_row_widgets.append(label)
        previous_time: datetime | None = None
        for message in messages:
            message_time = self._parse_message_time(message.get("created_at"))
            show_time = previous_time is None or (
                message_time is not None
                and previous_time is not None
                and abs((message_time - previous_time).total_seconds()) > 120
            )
            self._append_message(message, render_only=True, show_time=show_time, target=self.current_target)
            if message_time is not None:
                previous_time = message_time
        self._scroll_messages_to_latest(self.current_target)

    def _append_message(self, message: dict[str, Any], render_only: bool = False, show_time: bool = True, target: tuple[str, int] | None = None) -> None:
        if target is not None:
            self._activate_chat_window(target)
        if not self._chat_window_exists(self.current_target) or not hasattr(self, "message_content"):
            return
        mine = self.user and int(message["sender_id"]) == int(self.user["id"])
        row = self._build_message_row(message, bool(mine), show_time)
        row.pack(fill=tk.X, padx=0, pady=0)
        self.message_row_widgets.append(row)
        if not render_only:
            self._scroll_messages_to_latest(self.current_target)

    def _upsert_message(self, target: tuple[str, int], message: dict[str, Any]) -> tuple[list[dict[str, Any]], bool, bool]:
        previous = self.messages_by_target.get(target, [])
        message_id = int(message["id"])
        already_present = any(int(item["id"]) == message_id for item in previous)
        merged = self._merge_messages(previous, [message])
        self.messages_by_target[target] = merged
        appended_at_end = not already_present and bool(merged) and int(merged[-1]["id"]) == message_id
        return merged, already_present, appended_at_end

    def _show_current_message_update(
        self,
        target: tuple[str, int],
        message: dict[str, Any],
        messages: list[dict[str, Any]],
        already_present: bool,
        appended_at_end: bool,
    ) -> None:
        if not self._chat_window_exists(target):
            return
        self._activate_chat_window(target)
        if already_present:
            self._scroll_messages_to_latest(target)
            return
        if not appended_at_end:
            self._render_messages(messages, target)
            return
        previous_messages = messages[:-1]
        if not previous_messages:
            self._destroy_message_rows(target)
        self._append_message(message, show_time=self._should_show_message_time(previous_messages, message), target=target)

    def _should_show_message_time(self, previous_messages: list[dict[str, Any]], message: dict[str, Any]) -> bool:
        message_time = self._parse_message_time(message.get("created_at"))
        previous_time: datetime | None = None
        for previous in reversed(previous_messages):
            previous_time = self._parse_message_time(previous.get("created_at"))
            if previous_time is not None:
                break
        return previous_time is None or (
            message_time is not None
            and abs((message_time - previous_time).total_seconds()) > 120
        )

    def _destroy_message_rows(self, target: tuple[str, int] | None = None) -> None:
        if target is not None:
            self._activate_chat_window(target)
        for row in list(getattr(self, "message_row_widgets", [])):
            try:
                if row.winfo_exists():
                    row.destroy()
            except tk.TclError:
                continue
        self.message_row_widgets.clear()

    def _build_message_row(self, message: dict[str, Any], mine: bool, show_time: bool) -> tk.Frame:
        width = self._message_row_width()
        row = tk.Frame(self.message_content, bg="#f1f7ff", width=width)

        side = tk.RIGHT if mine else tk.LEFT
        cluster = tk.Frame(row, bg="#f1f7ff")
        cluster.pack(side=side, anchor=tk.E if mine else tk.W, padx=(90, 24) if mine else (24, 90), pady=(8, 10))

        avatar_value = (self.user or {}).get("avatar", "") if mine else message.get("sender_avatar", "")
        display_name = "我" if mine else self._message_sender_name(message)
        if not mine:
            avatar = tk.Canvas(cluster, width=42, height=42, bg="#f1f7ff", highlightthickness=0)
            avatar.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 8))
            self._draw_avatar(avatar, avatar_value, display_name, size=40, bg="#f1f7ff", fill="#60a5fa")
            message_target = self.current_target
            self._bind_click(avatar, lambda message=message, target=message_target: self._show_message_sender_profile(message, target))
        else:
            avatar = tk.Canvas(cluster, width=42, height=42, bg="#f1f7ff", highlightthickness=0)
            avatar.pack(side=tk.RIGHT, anchor=tk.N, padx=(8, 0))
            self._draw_avatar(avatar, avatar_value, display_name, size=40, bg="#f1f7ff", fill="#22c55e")

        stack = tk.Frame(cluster, bg="#f1f7ff")
        stack.pack(side=tk.LEFT if not mine else tk.RIGHT, anchor=tk.E if mine else tk.W)

        if not mine:
            tk.Label(
                stack,
                text=display_name,
                bg="#f1f7ff",
                fg="#64748b",
                font=("Microsoft YaHei UI", 9),
                anchor=tk.W,
            ).pack(anchor=tk.W, pady=(0, 2))

        bubble = tk.Frame(stack, bg="#c9f7d7" if mine else "#ffffff", padx=14, pady=10)
        bubble.pack(anchor=tk.E if mine else tk.W)
        bubble_max_width = max(240, min(560, width - 240))
        if message.get("message_type") in {"file", "image"} and message.get("file_id"):
            self._render_file_message_content(bubble, message, bubble_max_width)
        else:
            tk.Label(
                bubble,
                text=self._message_display_content(message),
                bg=bubble["bg"],
                fg="#111827",
                font=("Microsoft YaHei UI", 11),
                justify=tk.LEFT,
                wraplength=bubble_max_width,
            ).pack(anchor=tk.W)

        footer_parts = []
        if show_time and message.get("created_at"):
            footer_parts.append(self._format_message_time(str(message.get("created_at"))))
        if message.get("status") == "recalled":
            footer_parts.append("已撤回")
        if footer_parts:
            tk.Label(
                stack,
                text=" · ".join(footer_parts),
                bg="#f1f7ff",
                fg="#64748b",
                font=("Microsoft YaHei UI", 8),
            ).pack(anchor=tk.E if mine else tk.W, pady=(4, 0))

        return row

    def _message_row_width(self, target: tuple[str, int] | None = None) -> int:
        if target is not None:
            self._activate_chat_window(target)
        if not self._chat_window_exists(self.current_target) or not hasattr(self, "message_canvas"):
            return 760
        try:
            width = self.message_canvas.winfo_width()
        except tk.TclError:
            return 760
        return max(360, width)

    def _resize_message_rows(self, target: tuple[str, int] | None = None) -> None:
        if target is not None:
            self._activate_chat_window(target)
        width = self._message_row_width(self.current_target)
        for row in list(getattr(self, "message_row_widgets", [])):
            try:
                if row.winfo_exists():
                    row.configure(width=width)
            except tk.TclError:
                continue

    def _message_sender_name(self, message: dict[str, Any]) -> str:
        return str(message.get("sender_group_alias") or message.get("sender_nickname") or message.get("sender_username") or "对方")

    def _message_display_content(self, message: dict[str, Any]) -> str:
        return str(message.get("content", ""))

    def _render_file_message_content(self, bubble: tk.Frame, message: dict[str, Any], max_width: int) -> None:
        filename = str(message.get("file_name") or f"ochat_file_{message.get('file_id')}")
        kind, accent, fill = self._file_kind(filename, str(message.get("message_type", "file")))
        content = str(message.get("content", "")).strip()

        if message.get("message_type") == "image":
            self._render_inline_image_preview(bubble, message, max_width)

        card = tk.Frame(bubble, bg=fill, padx=10, pady=8, highlightthickness=1, highlightbackground=accent)
        card.pack(anchor=tk.W, fill=tk.X, pady=(0 if message.get("message_type") != "image" else 8, 0))
        badge = tk.Label(card, text=kind, bg=accent, fg="#ffffff", font=("Microsoft YaHei UI", 8, "bold"), padx=6, pady=2)
        badge.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 8))
        info = tk.Frame(card, bg=fill)
        info.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            info,
            text=filename,
            bg=fill,
            fg="#111827",
            font=("Microsoft YaHei UI", 10, "bold"),
            justify=tk.LEFT,
            wraplength=max_width,
        ).pack(anchor=tk.W)
        if content:
            tk.Label(
                info,
                text=content,
                bg=fill,
                fg="#475569",
                font=("Microsoft YaHei UI", 9),
                justify=tk.LEFT,
                wraplength=max_width,
            ).pack(anchor=tk.W, pady=(4, 0))
        link = tk.Label(
            info,
            text="下载文件",
            bg=fill,
            fg="#2563eb",
            cursor="hand2",
            font=("Microsoft YaHei UI", 9, "underline"),
        )
        link.pack(anchor=tk.W, pady=(6, 0))
        link.bind("<Button-1>", lambda _event, msg=message: self._download_file_message(msg))

    def _render_inline_image_preview(self, bubble: tk.Frame, message: dict[str, Any], max_width: int) -> None:
        key = f"inline:{int(message['file_id'])}"
        image = self.inline_images.get(key)
        if image is not None:
            tk.Label(bubble, image=image, bg=bubble["bg"]).pack(anchor=tk.W, pady=(0, 8))
            return

        text = "图片加载失败，仍可下载文件" if key in self.inline_image_failed else "图片加载中..."
        placeholder = tk.Label(
            bubble,
            text=text,
            bg="#f8fafc",
            fg="#64748b",
            font=("Microsoft YaHei UI", 9),
            width=28,
            height=6,
            relief=tk.FLAT,
        )
        placeholder.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))
        if key in self.inline_image_failed:
            return

        def update_preview() -> None:
            if not placeholder.winfo_exists():
                return
            loaded = self.inline_images.get(key)
            if loaded is None:
                placeholder.configure(text="图片加载失败，仍可下载文件")
                return
            placeholder.configure(image=loaded, text="", width=0, height=0, bg=bubble["bg"])
            placeholder.image = loaded  # type: ignore[attr-defined]

        self._load_inline_image_async(message, update_preview)

    def _load_inline_image_async(self, message: dict[str, Any], on_loaded: Callable[[], None]) -> None:
        file_id = int(message["file_id"])
        key = f"inline:{file_id}"
        if key in self.inline_images or key in self.inline_image_failed:
            on_loaded()
            return
        self.inline_image_waiters.setdefault(key, []).append(on_loaded)
        if key in self.inline_image_loading:
            return
        self.inline_image_loading.add(key)
        filename = str(message.get("file_name") or f"ochat_file_{file_id}")
        target = self._cached_file_path(file_id, filename)

        def worker() -> None:
            try:
                if not target.exists():
                    self.client.download_file(file_id, target)
                self.after(0, lambda: self._finish_inline_image_load(key, target))
            except Exception:
                self.after(0, lambda: self._finish_inline_image_load(key, None))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_inline_image_load(self, key: str, path: Path | None) -> None:
        try:
            if path is not None and path.exists():
                image = tk.PhotoImage(file=str(path))
                max_side = max(image.width(), image.height())
                if max_side > 320:
                    factor = max(1, (max_side + 319) // 320)
                    image = image.subsample(factor, factor)
                self.inline_images[key] = image
        except tk.TclError:
            self.inline_image_failed.add(key)
        if key not in self.inline_images:
            self.inline_image_failed.add(key)
        self.inline_image_loading.discard(key)
        callbacks = self.inline_image_waiters.pop(key, [])
        for callback in callbacks:
            callback()

    def _cached_file_path(self, file_id: int, filename: str) -> Path:
        safe_name = Path(filename or f"ochat_file_{file_id}").name or f"ochat_file_{file_id}"
        return self.file_cache_dir / f"{file_id}_{safe_name}"

    @staticmethod
    def _file_kind(filename: str, message_type: str) -> tuple[str, str, str]:
        suffix = Path(filename).suffix.lower()
        if message_type == "image" or suffix in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}:
            return ("图片", "#0ea5e9", "#e0f2fe")
        if suffix in {".doc", ".docx", ".pdf", ".txt", ".md"}:
            return ("文档", "#2563eb", "#dbeafe")
        if suffix in {".xls", ".xlsx", ".csv"}:
            return ("表格", "#16a34a", "#dcfce7")
        if suffix in {".zip", ".rar", ".7z"}:
            return ("压缩包", "#9333ea", "#f3e8ff")
        if suffix in {".py", ".js", ".html", ".css", ".json", ".sql"}:
            return ("代码", "#475569", "#e2e8f0")
        return ("文件", "#64748b", "#f1f5f9")

    @staticmethod
    def _parse_message_time(value: Any) -> datetime | None:
        if not value:
            return None
        text = str(value)
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(text[:19], fmt)
            except ValueError:
                continue
        return None

    def _format_message_time(self, value: str) -> str:
        parsed = self._parse_message_time(value)
        if parsed is None:
            return value
        return parsed.strftime("%Y-%m-%d %H:%M")

    def _scroll_messages_to_latest(self, target: tuple[str, int] | None = None) -> None:
        if target is not None:
            if not self._chat_window_exists(target):
                return
            self._activate_chat_window(target)
        if not self._chat_window_exists(self.current_target) or not hasattr(self, "message_canvas"):
            return
        canvas = self.message_canvas
        content = self.message_content

        def scroll(remaining: int = 3) -> None:
            try:
                if canvas.winfo_exists():
                    content.update_idletasks()
                    bbox = canvas.bbox("all")
                    if bbox:
                        canvas.configure(scrollregion=bbox)
                    canvas.yview_moveto(1.0)
            except tk.TclError:
                return
            if remaining > 0:
                canvas.after(40, lambda: scroll(remaining - 1))

        canvas.after_idle(scroll)

    def _send_from_text(self, event: tk.Event, target: tuple[str, int] | None = None) -> str | None:
        if event.state & 0x0001:
            return None
        self._send_message(target)
        return "break"

    def _send_message(self, target: tuple[str, int] | None = None) -> None:
        target = target or self.current_target
        if not target:
            messagebox.showinfo("提示", "请先选择聊天对象")
            return
        self._activate_chat_window(target)
        if not self._chat_window_exists(target) or not hasattr(self, "input_text"):
            messagebox.showinfo("提示", "请先打开聊天窗口")
            return
        content = self.input_text.get("1.0", "end-1c").strip()
        if not content:
            return
        self.input_text.delete("1.0", tk.END)
        kind, target_id = target
        if kind == "direct":
            self._run_request(lambda: self.client.request("messages.direct.send", receiver_id=target_id, content=content), self._on_message_sent)
        else:
            self._run_request(lambda: self.client.request("messages.group.send", group_id=target_id, content=content), self._on_message_sent)

    def _on_message_sent(self, response: dict[str, Any]) -> None:
        message = response.get("message")
        if not isinstance(message, dict):
            self._scroll_messages_to_latest()
            return
        target = self._target_for_message(message)
        messages, already_present, appended_at_end = self._upsert_message(target, message)
        if self._chat_window_exists(target):
            self._show_current_message_update(target, message, messages, already_present, appended_at_end)
        else:
            self._scroll_messages_to_latest(target)

    def _insert_emoji(self, target: tuple[str, int] | None = None) -> None:
        target = target or self.current_target
        if target is not None:
            self._activate_chat_window(target)
        if hasattr(self, "emoji_window") and self.emoji_window.winfo_exists():
            if getattr(self, "emoji_target", None) == target:
                self.emoji_window.lift()
                self.emoji_window.focus_force()
                return
            self.emoji_window.destroy()

        window = tk.Toplevel(self)
        self.emoji_window = window
        self.emoji_target = target
        window.title("表情包")
        window.configure(bg="#ffffff")
        window.resizable(False, False)
        window.transient(self)

        x = self.winfo_rootx() + max(self.winfo_width() - 430, 80)
        y = self.winfo_rooty() + max(self.winfo_height() - 390, 80)
        window.geometry(f"390x320+{x}+{y}")

        def insert_emoji(value: str) -> None:
            if not value:
                return
            if target is not None:
                self._activate_chat_window(target)
            if not target or not self._chat_window_exists(target) or not hasattr(self, "input_text"):
                window.destroy()
                return
            self.input_text.insert(tk.INSERT, value)
            self.input_text.focus_set()

        notebook = ttk.Notebook(window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 8))

        for category, emojis in EMOJI_CATEGORIES:
            page = tk.Frame(notebook, bg="#ffffff")
            notebook.add(page, text=category)
            for index, emoji in enumerate(emojis):
                button = tk.Button(
                    page,
                    text=emoji,
                    width=3,
                    height=1,
                    bd=0,
                    bg="#f7f9fc",
                    activebackground="#e7edf5",
                    font=("Segoe UI Emoji", 16),
                    command=lambda emoji=emoji: insert_emoji(emoji),
                )
                button.grid(row=index // 8, column=index % 8, padx=4, pady=4, ipadx=2, ipady=2)

        custom = tk.Frame(window, bg="#ffffff")
        custom.pack(fill=tk.X, padx=12, pady=(0, 12))
        tk.Label(custom, text="自定义", bg="#ffffff", fg="#64748b").pack(side=tk.LEFT, padx=(0, 8))
        custom_entry = ttk.Entry(custom)
        custom_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        custom_entry.focus_set()

        def insert_custom() -> None:
            insert_emoji(custom_entry.get().strip())
            custom_entry.delete(0, tk.END)

        ttk.Button(custom, text="插入", command=insert_custom).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(custom, text="关闭", command=window.destroy).pack(side=tk.LEFT, padx=(8, 0))
        custom_entry.bind("<Return>", lambda _event: insert_custom())

    def _send_file(self, target: tuple[str, int] | None = None) -> None:
        target = target or self.current_target
        if not target:
            messagebox.showinfo("提示", "请先选择聊天对象")
            return
        self._activate_chat_window(target)
        path = filedialog.askopenfilename(title="选择文件或图片")
        if not path:
            return
        kind, target_id = target

        def job() -> dict[str, Any]:
            upload = self.client.upload_file(path)
            file_record = upload["file"]
            message_type = "image" if Path(path).suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"} else "file"
            content = f"已发送 {Path(path).name}"
            if kind == "direct":
                return self.client.request("messages.direct.send", receiver_id=target_id, content=content, message_type=message_type, file_id=file_record["id"])
            return self.client.request("messages.group.send", group_id=target_id, content=content, message_type=message_type, file_id=file_record["id"])

        self._run_request(job, self._on_message_sent)

    def _download_latest_file(self, target: tuple[str, int] | None = None) -> None:
        target = target or self.current_target
        if not target:
            messagebox.showinfo("提示", "请先选择聊天对象")
            return
        file_messages = self._file_messages_for_current_target(target)
        if not file_messages:
            messagebox.showinfo("提示", "当前聊天没有可保存的文件")
            return
        if len(file_messages) == 1:
            self._download_file_message(file_messages[0])
            return
        self._show_file_download_window(file_messages)

    def _file_messages_for_current_target(self, target: tuple[str, int] | None = None) -> list[dict[str, Any]]:
        target = target or self.current_target
        if not target:
            return []
        messages = self.messages_by_target.get(target, [])
        return [message for message in messages if message.get("file_id")]

    def _download_file_message(self, message: dict[str, Any]) -> None:
        file_id = int(message["file_id"])
        filename = str(message.get("file_name") or f"ochat_file_{file_id}")
        save_path = filedialog.asksaveasfilename(title="保存文件", initialfile=filename)
        if not save_path:
            return
        self._run_request(lambda: self.client.download_file(file_id, save_path), lambda _resp: messagebox.showinfo("保存成功", f"文件已保存到：{save_path}"))

    def _show_file_download_window(self, file_messages: list[dict[str, Any]]) -> None:
        window = tk.Toplevel(self)
        window.title("保存文件")
        window.geometry("460x320")
        window.minsize(420, 280)
        window.configure(bg="#ffffff")
        window.transient(self)

        tk.Label(window, text="选择要保存的文件", bg="#ffffff", fg="#121826", font=("Microsoft YaHei UI", 13, "bold")).pack(anchor=tk.W, padx=16, pady=(16, 8))

        listbox = tk.Listbox(window, activestyle="dotbox", height=10)
        listbox.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))
        for message in reversed(file_messages):
            sender = "我" if self.user and int(message.get("sender_id", 0)) == int(self.user["id"]) else message.get("sender_nickname") or message.get("sender_username") or "对方"
            filename = message.get("file_name") or f"ochat_file_{message.get('file_id')}"
            listbox.insert(tk.END, f"{filename}  |  {sender}  |  {message.get('created_at', '')}")
        listbox.selection_set(0)

        ordered_messages = list(reversed(file_messages))

        def download_selected() -> None:
            selection = listbox.curselection()
            if not selection:
                messagebox.showinfo("提示", "请选择一个文件", parent=window)
                return
            message = ordered_messages[int(selection[0])]
            window.destroy()
            self._download_file_message(message)

        actions = tk.Frame(window, bg="#ffffff")
        actions.pack(fill=tk.X, padx=16, pady=(0, 16))
        ttk.Button(actions, text="保存选中文件", command=download_selected).pack(side=tk.RIGHT)
        ttk.Button(actions, text="取消", command=window.destroy).pack(side=tk.RIGHT, padx=(0, 8))
        listbox.bind("<Double-Button-1>", lambda _event: download_selected())

    def _recall_last_message(self, target: tuple[str, int] | None = None) -> None:
        target = target or self.current_target
        if not target or not self.user:
            messagebox.showinfo("提示", "请先选择聊天对象")
            return
        messages = self.messages_by_target.get(target, [])
        mine = [msg for msg in messages if int(msg.get("sender_id", 0)) == int(self.user["id"]) and msg.get("status") != "recalled"]
        if not mine:
            messagebox.showinfo("提示", "当前聊天没有可撤回的自己消息")
            return
        self._run_request(lambda: self.client.request("messages.recall", message_id=int(mine[-1]["id"])), lambda _resp: None)

    def _add_friend(self) -> None:
        username = simpledialog.askstring("添加好友", "请输入对方用户名", parent=self)
        if not username:
            return
        message = simpledialog.askstring("好友申请", "验证消息（可留空）", parent=self) or ""
        self._run_request(
            lambda: self.client.request("friends.request", username=username.strip(), message=message),
            lambda _resp: self._request_sent("好友申请已发送"),
        )

    def _edit_friend(self) -> None:
        if not self.current_target or self.current_target[0] != "direct":
            messagebox.showinfo("提示", "请先选择一个好友")
            return
        friend_id = self.current_target[1]
        friend = next((item for item in self.friends if int(item["id"]) == friend_id), None)
        if not friend:
            return
        remark = simpledialog.askstring("修改备注", "备注", initialvalue=friend.get("remark", ""), parent=self) or ""
        group_name = simpledialog.askstring("好友分组", "分组", initialvalue=friend.get("group_name", "Friends"), parent=self) or "Friends"
        self._run_request(lambda: self.client.request("friends.update", friend_id=friend_id, remark=remark, group_name=group_name), lambda _resp: self._reload_all_lists())

    def _remove_friend(self) -> None:
        if not self.current_target or self.current_target[0] != "direct":
            messagebox.showinfo("提示", "请先选择一个好友")
            return
        if not messagebox.askyesno("删除好友", "确认删除该好友？"):
            return
        self._run_request(lambda: self.client.request("friends.remove", friend_id=self.current_target[1]), lambda _resp: self._reload_all_lists())

    def _create_group(self) -> None:
        name = simpledialog.askstring("创建群聊", "群聊名称", parent=self)
        if not name:
            return
        self._run_request(lambda: self.client.request("groups.create", name=name.strip()), lambda _resp: self._reload_all_lists())

    def _invite_member(self, target: tuple[str, int] | None = None) -> None:
        target = target or self.current_target
        if not target or target[0] != "group":
            messagebox.showinfo("提示", "请先选择群聊")
            return
        self._invite_group_member(target[1], self, lambda: None)

    def _invite_group_member(self, group_id: int, parent: tk.Widget, after_success: Callable[[], None]) -> None:
        username = simpledialog.askstring("邀请成员", "请输入用户名", parent=parent)
        if not username:
            return
        message = simpledialog.askstring("群邀请", "邀请说明（可留空）", parent=parent) or ""
        self._run_request(
            lambda: self.client.request("groups.invite.request", group_id=group_id, username=username.strip(), message=message),
            lambda _resp: (self._request_sent("群邀请已发送"), after_success()),
        )

    def _request_sent(self, text: str) -> None:
        messagebox.showinfo("已发送", text)
        self._reload_requests()

    def _respond_friend_request(self, item: dict[str, Any]) -> None:
        name = item.get("requester_nickname") or item.get("requester_username")
        choice = messagebox.askyesnocancel("好友申请", f"是否同意 {name} 的好友申请？")
        if choice is None:
            return
        remark = ""
        if choice:
            remark = simpledialog.askstring("好友备注", "备注（可留空）", initialvalue=name, parent=self) or ""
        self._run_request(
            lambda: self.client.request("friends.requests.respond", friend_request_id=item["id"], accept=choice, remark=remark),
            lambda _resp: self._reload_all_lists(),
        )

    def _respond_group_invitation(self, item: dict[str, Any]) -> None:
        group_name = item.get("group_name")
        choice = messagebox.askyesnocancel("群邀请", f"是否加入群聊“{group_name}”？")
        if choice is None:
            return
        self._run_request(
            lambda: self.client.request("groups.invitations.respond", invitation_id=item["id"], accept=choice),
            lambda _resp: self._reload_all_lists(),
        )

    def _show_members(self, target: tuple[str, int] | None = None) -> None:
        target = target or self.current_target
        if not target or target[0] != "group":
            messagebox.showinfo("提示", "请先选择群聊")
            return
        group_id = target[1]
        window = tk.Toplevel(self)
        window.title("群面板")
        window.geometry("680x560")
        window.minsize(620, 500)
        window.configure(bg="#ffffff")
        window.transient(self)

        self._reload_group_panel(window, group_id)

    def _reload_group_panel(self, window: tk.Toplevel, group_id: int) -> None:
        if not window.winfo_exists():
            return

        def show(response: dict[str, Any]) -> None:
            if not window.winfo_exists():
                return
            self._render_group_panel(window, response.get("group", {}), response.get("members", []))

        self._run_request(lambda: self.client.request("groups.members", group_id=group_id), show)

    def _render_group_panel(self, window: tk.Toplevel, group: dict[str, Any], members: list[dict[str, Any]]) -> None:
        for child in window.winfo_children():
            child.destroy()
        group_id = int(group["id"])
        my_role = str(group.get("my_role", "member"))
        my_id = int((self.user or {}).get("id", 0))

        header = tk.Frame(window, bg="#ffffff")
        header.pack(fill=tk.X, padx=22, pady=(20, 10))
        title_row = tk.Frame(header, bg="#ffffff")
        title_row.pack(fill=tk.X)
        tk.Label(title_row, text=str(group.get("name", "群聊")), bg="#ffffff", fg="#121826", font=("Microsoft YaHei UI", 18, "bold")).pack(side=tk.LEFT)
        tk.Label(
            title_row,
            text=f"{len(members)} 人 · 我的身份：{self._group_role_label(my_role)}",
            bg="#ffffff",
            fg="#64748b",
            font=("Microsoft YaHei UI", 10),
        ).pack(side=tk.LEFT, padx=(12, 0))
        group_remark = str(group.get("group_remark") or "")
        remark_text = f"我的群备注：{group_remark}" if group_remark else "我的群备注：未设置"
        tk.Label(header, text=remark_text, bg="#ffffff", fg="#64748b", font=("Microsoft YaHei UI", 10), anchor=tk.W).pack(fill=tk.X, pady=(8, 0))
        my_alias = str(group.get("my_alias") or "")
        alias_text = f"我的群昵称：{my_alias}" if my_alias else "我的群昵称：未设置"
        tk.Label(header, text=alias_text, bg="#ffffff", fg="#64748b", font=("Microsoft YaHei UI", 10), anchor=tk.W).pack(fill=tk.X, pady=(4, 0))

        actions = tk.Frame(header, bg="#ffffff")
        actions.pack(fill=tk.X, pady=(14, 0))
        if my_role in {"owner", "admin"}:
            ttk.Button(actions, text="邀请成员", command=lambda: self._invite_group_member(group_id, window, lambda: self._reload_group_panel(window, group_id))).pack(side=tk.LEFT)
            ttk.Button(actions, text="修改群名", command=lambda: self._rename_group(window, group)).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="搜索消息", command=self._search_messages).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="我的群昵称", command=lambda: self._update_group_member_alias(window, group_id, self._current_group_member(members, my_id))).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="修改备注", command=lambda: self._update_group_remark(window, group)).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="刷新", command=lambda: self._reload_group_panel(window, group_id)).pack(side=tk.LEFT, padx=(8, 0))
        if my_role == "owner":
            ttk.Button(actions, text="解散群聊", command=lambda: self._dismiss_group(window, group_id)).pack(side=tk.RIGHT)
        ttk.Button(actions, text="退出群聊", command=lambda: self._leave_group(window, group_id, my_role)).pack(side=tk.RIGHT, padx=(0, 8))

        divider = tk.Frame(window, bg="#e5e7eb", height=1)
        divider.pack(fill=tk.X, padx=22, pady=(0, 10))

        body = tk.Frame(window, bg="#ffffff")
        body.pack(fill=tk.BOTH, expand=True, padx=22, pady=(0, 20))
        canvas = tk.Canvas(body, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(body, orient=tk.VERTICAL, command=canvas.yview)
        list_frame = tk.Frame(canvas, bg="#ffffff")
        list_window = canvas.create_window((0, 0), window=list_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        list_frame.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(list_window, width=event.width))
        self._bind_canvas_mousewheel(canvas)

        for member in members:
            self._add_group_member_row(list_frame, group_id, member, my_id, my_role, window)

    @staticmethod
    def _current_group_member(members: list[dict[str, Any]], my_id: int) -> dict[str, Any]:
        return next((member for member in members if int(member["id"]) == my_id), {"id": my_id, "alias": ""})

    @staticmethod
    def _group_role_label(role: str) -> str:
        return {"owner": "群主", "admin": "管理员", "member": "成员"}.get(role, role)

    def _add_group_member_row(
        self,
        parent: tk.Widget,
        group_id: int,
        member: dict[str, Any],
        my_id: int,
        my_role: str,
        panel: tk.Toplevel,
    ) -> None:
        member_id = int(member["id"])
        role = str(member.get("role", "member"))
        profile_name = member.get("nickname") or member.get("username")
        name = member.get("alias") or profile_name
        row = tk.Frame(parent, bg="#ffffff", highlightthickness=1, highlightbackground="#edf0f5")
        row.pack(fill=tk.X, pady=4)

        avatar = tk.Canvas(row, width=42, height=48, bg="#ffffff", highlightthickness=0)
        avatar.pack(side=tk.LEFT, padx=(10, 8), pady=8)
        self._draw_avatar(avatar, member.get("avatar", ""), str(name), size=42, bg="#ffffff", fill="#60a5fa" if role != "owner" else "#22c55e")
        self._bind_click(avatar, lambda member=member: self._show_user_profile(member, title="成员资料", parent=panel))

        info = tk.Frame(row, bg="#ffffff")
        info.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8)
        tk.Label(info, text=str(name), bg="#ffffff", fg="#111827", font=("Microsoft YaHei UI", 10, "bold"), anchor=tk.W).pack(anchor=tk.W)
        meta = f"{member.get('username')} · {self._group_role_label(role)}"
        if member.get("alias"):
            meta += f" · 原昵称：{profile_name}"
        if member_id == my_id:
            meta += " · 我"
        tk.Label(info, text=meta, bg="#ffffff", fg="#64748b", font=("Microsoft YaHei UI", 9), anchor=tk.W).pack(anchor=tk.W, pady=(4, 0))

        tools = tk.Frame(row, bg="#ffffff")
        tools.pack(side=tk.RIGHT, padx=10)
        if member_id == my_id or my_role in {"owner", "admin"}:
            button_text = "我的群昵称" if member_id == my_id else "群昵称"
            ttk.Button(tools, text=button_text, command=lambda: self._update_group_member_alias(panel, group_id, member)).pack(side=tk.LEFT, padx=(0, 6))
        if member_id == my_id:
            return
        if my_role == "owner" and role != "owner":
            next_role = "member" if role == "admin" else "admin"
            text = "取消管理员" if role == "admin" else "设为管理员"
            ttk.Button(
                tools,
                text=text,
                command=lambda: self._set_group_member_role(panel, group_id, member_id, next_role),
            ).pack(side=tk.LEFT, padx=(0, 6))
            ttk.Button(tools, text="移出", command=lambda: self._remove_group_member(panel, group_id, member_id, name)).pack(side=tk.LEFT)
        elif my_role == "admin" and role == "member":
            ttk.Button(tools, text="移出", command=lambda: self._remove_group_member(panel, group_id, member_id, name)).pack(side=tk.LEFT)

    def _set_group_member_role(self, panel: tk.Toplevel, group_id: int, member_id: int, role: str) -> None:
        self._run_request(
            lambda: self.client.request("groups.member_role.update", group_id=group_id, member_id=member_id, role=role),
            lambda _resp: self._reload_group_panel(panel, group_id),
        )

    def _update_group_member_alias(self, panel: tk.Toplevel, group_id: int, member: dict[str, Any]) -> None:
        member_id = int(member["id"])
        current_alias = str(member.get("alias") or "")
        name = member.get("nickname") or member.get("username")
        alias = simpledialog.askstring("修改群昵称", f"{name} 的群昵称", initialvalue=current_alias, parent=panel)
        if alias is None:
            return
        self._run_request(
            lambda: self.client.request("groups.member_alias.update", group_id=group_id, member_id=member_id, alias=alias.strip()),
            lambda _resp: (self._reload_group_panel(panel, group_id), self._reload_all_lists()),
        )

    def _remove_group_member(self, panel: tk.Toplevel, group_id: int, member_id: int, name: Any) -> None:
        if not messagebox.askyesno("移出成员", f"确认将 {name} 移出群聊？", parent=panel):
            return
        self._run_request(
            lambda: self.client.request("groups.remove_member", group_id=group_id, member_id=member_id),
            lambda _resp: (self._reload_group_panel(panel, group_id), self._reload_all_lists()),
        )

    def _rename_group(self, panel: tk.Toplevel, group: dict[str, Any]) -> None:
        group_id = int(group["id"])
        name = simpledialog.askstring("修改群名", "群聊名称", initialvalue=str(group.get("name", "")), parent=panel)
        if not name:
            return
        self._run_request(
            lambda: self.client.request("groups.rename", group_id=group_id, name=name.strip()),
            lambda _resp: (self._reload_group_panel(panel, group_id), self._reload_all_lists()),
        )

    def _update_group_remark(self, panel: tk.Toplevel, group: dict[str, Any]) -> None:
        group_id = int(group["id"])
        current_remark = str(group.get("group_remark") or "")
        group_remark = simpledialog.askstring("修改群备注", "备注这个群是做什么的", initialvalue=current_remark, parent=panel)
        if group_remark is None:
            return
        self._run_request(
            lambda: self.client.request("groups.remark.update", group_id=group_id, group_remark=group_remark.strip()),
            lambda _resp: (self._reload_group_panel(panel, group_id), self._reload_all_lists()),
        )

    def _leave_group(self, panel: tk.Toplevel, group_id: int, my_role: str) -> None:
        prompt = "你是群主，退出后会按管理员任命顺序自动转让群主。确认退出？" if my_role == "owner" else "确认退出该群聊？"
        if not messagebox.askyesno("退出群聊", prompt, parent=panel):
            return

        def left(_response: dict[str, Any]) -> None:
            panel.destroy()
            if self.current_target == ("group", group_id):
                self.current_target = None
                self.current_title = "请选择会话"
                self.current_subtitle = "从左侧会话、好友或群聊开始"
                self._close_chat_window(("group", group_id), clear_target=False)
            self._reload_all_lists()

        self._run_request(lambda: self.client.request("groups.leave", group_id=group_id), left)

    def _dismiss_group(self, panel: tk.Toplevel, group_id: int) -> None:
        if not messagebox.askyesno("解散群聊", "解散后所有成员都会退出该群聊，确认解散？", parent=panel):
            return

        def dismissed(_response: dict[str, Any]) -> None:
            panel.destroy()
            if self.current_target == ("group", group_id):
                self.current_target = None
                self.current_title = "请选择会话"
                self.current_subtitle = "从左侧会话、好友或群聊开始"
                self._close_chat_window(("group", group_id), clear_target=False)
            self._reload_all_lists()

        self._run_request(lambda: self.client.request("groups.dismiss", group_id=group_id), dismissed)

    def _edit_profile(self) -> None:
        if not self.user:
            return
        window = tk.Toplevel(self)
        window.title("个人资料")
        window.geometry("520x560")
        window.minsize(480, 520)
        window.configure(bg="#ffffff")
        window.transient(self)
        window.grab_set()

        header = tk.Frame(window, bg="#ffffff")
        header.pack(fill=tk.X, padx=28, pady=(24, 12))
        tk.Label(header, text="个人资料", bg="#ffffff", fg="#121826", font=("Microsoft YaHei UI", 18, "bold")).pack(anchor=tk.W)
        tk.Label(header, text="UID 和用户名不可修改，其余资料可随时更新", bg="#ffffff", fg="#64748b").pack(anchor=tk.W, pady=(4, 0))

        body = tk.Frame(window, bg="#ffffff")
        body.pack(fill=tk.BOTH, expand=True, padx=(28, 20), pady=8)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        profile_canvas = tk.Canvas(body, bg="#ffffff", bd=0, highlightthickness=0)
        profile_scrollbar = ttk.Scrollbar(body, orient=tk.VERTICAL, command=profile_canvas.yview)
        profile_canvas.configure(yscrollcommand=profile_scrollbar.set)
        profile_canvas.grid(row=0, column=0, sticky="nsew")
        profile_scrollbar.grid(row=0, column=1, sticky="ns", padx=(8, 0))

        form = tk.Frame(profile_canvas, bg="#ffffff")
        form_window = profile_canvas.create_window((0, 0), window=form, anchor=tk.NW)
        form.columnconfigure(1, weight=1)
        form.bind("<Configure>", lambda _event: profile_canvas.configure(scrollregion=profile_canvas.bbox("all")))
        profile_canvas.bind("<Configure>", lambda event: profile_canvas.itemconfigure(form_window, width=event.width))
        self._bind_canvas_mousewheel(profile_canvas)

        entries: dict[str, tk.Widget] = {}

        def add_row(row: int, label: str, key: str, value: Any = "", readonly: bool = False) -> None:
            tk.Label(form, text=label, bg="#ffffff", fg="#374151", anchor=tk.W).grid(row=row, column=0, sticky="w", pady=7)
            entry = ttk.Entry(form)
            entry.insert(0, "" if value is None else str(value))
            if readonly:
                entry.configure(state="readonly")
            entry.grid(row=row, column=1, sticky="ew", padx=(18, 0), pady=7)
            entries[key] = entry

        add_row(0, "UID", "uid", self.user.get("id"), readonly=True)
        add_row(1, "用户名", "username", self.user.get("username"), readonly=True)
        add_row(2, "昵称", "nickname", self.user.get("nickname", ""))

        tk.Label(form, text="性别", bg="#ffffff", fg="#374151", anchor=tk.W).grid(row=3, column=0, sticky="w", pady=7)
        gender = ttk.Combobox(form, values=("保密", "男", "女", "其他"), state="readonly")
        gender.set(self.user.get("gender") or "保密")
        gender.grid(row=3, column=1, sticky="ew", padx=(18, 0), pady=7)
        entries["gender"] = gender

        add_row(4, "生日", "birthday", self.user.get("birthday", ""))
        add_row(5, "年龄", "age", self.user.get("age") or "")
        add_row(6, "联系方式", "contact", self.user.get("contact", ""))

        tk.Label(form, text="头像", bg="#ffffff", fg="#374151", anchor=tk.W).grid(row=7, column=0, sticky="nw", pady=7)
        avatar_box = tk.Frame(form, bg="#ffffff")
        avatar_box.grid(row=7, column=1, sticky="ew", padx=(18, 0), pady=7)
        avatar_preview = tk.Canvas(avatar_box, width=64, height=64, bg="#ffffff", highlightthickness=0)
        avatar_preview.pack(side=tk.LEFT)
        self._draw_avatar(
            avatar_preview,
            self.user.get("avatar", ""),
            self.user.get("nickname") or self.user.get("username", "O"),
            size=64,
            bg="#ffffff",
            fill="#22c55e",
        )
        avatar_controls = tk.Frame(avatar_box, bg="#ffffff")
        avatar_controls.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(14, 0))
        avatar_entry = ttk.Entry(avatar_controls)
        avatar_entry.insert(0, self.user.get("avatar", "") or "")
        avatar_entry.configure(state="readonly")
        avatar_entry.pack(fill=tk.X)
        avatar_actions = tk.Frame(avatar_controls, bg="#ffffff")
        avatar_actions.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(avatar_actions, text="选择图片", command=lambda: self._choose_profile_avatar(window, avatar_entry, avatar_preview)).pack(side=tk.LEFT)
        ttk.Button(avatar_actions, text="清除头像", command=lambda: self._set_profile_avatar_entry(avatar_entry, avatar_preview, "")).pack(side=tk.LEFT, padx=(8, 0))
        entries["avatar"] = avatar_entry

        tk.Label(form, text="住址", bg="#ffffff", fg="#374151", anchor=tk.W).grid(row=8, column=0, sticky="nw", pady=7)
        address = tk.Text(form, height=3, wrap=tk.WORD, relief=tk.FLAT, bg="#f7f9fc", padx=8, pady=6)
        address.insert("1.0", self.user.get("address", "") or "")
        address.grid(row=8, column=1, sticky="ew", padx=(18, 0), pady=7)
        entries["address"] = address

        tk.Label(form, text="签名", bg="#ffffff", fg="#374151", anchor=tk.W).grid(row=9, column=0, sticky="nw", pady=7)
        signature = tk.Text(form, height=4, wrap=tk.WORD, relief=tk.FLAT, bg="#f7f9fc", padx=8, pady=6)
        signature.insert("1.0", self.user.get("signature", "") or "")
        signature.grid(row=9, column=1, sticky="ew", padx=(18, 0), pady=7)
        entries["signature"] = signature

        actions = tk.Frame(window, bg="#ffffff")
        actions.pack(fill=tk.X, padx=28, pady=(8, 24))
        ttk.Button(actions, text="取消", command=window.destroy).pack(side=tk.RIGHT)
        ttk.Button(actions, text="保存资料", style="Accent.TButton", command=lambda: self._save_profile_window(window, entries)).pack(side=tk.RIGHT, padx=(0, 10))

    def _choose_profile_avatar(self, parent: tk.Widget, entry: ttk.Entry, preview: tk.Canvas) -> None:
        path = filedialog.askopenfilename(
            title="选择头像图片",
            parent=parent,
            filetypes=(("PNG/GIF 图片", "*.png *.gif"), ("PNG 图片", "*.png"), ("GIF 图片", "*.gif")),
        )
        if not path:
            return
        self._set_profile_avatar_entry(entry, preview, path)

    def _set_profile_avatar_entry(self, entry: ttk.Entry, preview: tk.Canvas, value: str) -> None:
        entry.configure(state=tk.NORMAL)
        entry.delete(0, tk.END)
        entry.insert(0, value)
        entry.configure(state="readonly")
        initial = (self.user or {}).get("nickname") or (self.user or {}).get("username", "O")
        self._draw_avatar(preview, value if value.startswith("file:") else "", initial, size=64, bg="#ffffff", fill="#22c55e")
        if value and not value.startswith("file:"):
            self._draw_local_avatar_preview(preview, value, initial)

    def _draw_local_avatar_preview(self, canvas: tk.Canvas, path: str, initial: str) -> None:
        try:
            source = tk.PhotoImage(file=path)
            image = self._make_circular_avatar_image(source, 64)
            key = f"local:{path}:64"
            self.avatar_images[key] = image
            canvas.delete("all")
            canvas.create_image(32, 32, image=image)
        except tk.TclError:
            self._draw_avatar(canvas, "", initial, size=64, bg="#ffffff", fill="#22c55e")

    def _entry_value(self, widget: tk.Widget) -> str:
        if isinstance(widget, tk.Text):
            return widget.get("1.0", "end-1c").strip()
        return str(widget.get()).strip()  # type: ignore[attr-defined]

    def _save_profile_window(self, window: tk.Toplevel, entries: dict[str, tk.Widget]) -> None:
        nickname = self._entry_value(entries["nickname"]) or (self.user or {}).get("username", "")
        age_text = self._entry_value(entries["age"])
        age: int | str = ""
        if age_text:
            try:
                age = int(age_text)
            except ValueError:
                messagebox.showinfo("提示", "年龄必须是数字", parent=window)
                return
        payload = {
            "nickname": nickname,
            "gender": self._entry_value(entries["gender"]),
            "birthday": self._entry_value(entries["birthday"]),
            "age": age,
            "contact": self._entry_value(entries["contact"]),
            "avatar": self._entry_value(entries["avatar"]),
            "address": self._entry_value(entries["address"]),
            "signature": self._entry_value(entries["signature"]),
        }

        def job() -> dict[str, Any]:
            profile_payload = dict(payload)
            avatar_value = str(profile_payload.get("avatar", "")).strip()
            avatar_path = Path(avatar_value)
            if avatar_value and not avatar_value.startswith("file:") and avatar_path.is_file():
                upload = self.client.upload_file(avatar_path)
                profile_payload["avatar"] = f"file:{upload['file']['id']}"
            return self.client.request("profile.update", **profile_payload)

        def saved(response: dict[str, Any]) -> None:
            window.destroy()
            self._profile_updated(response["user"])
            messagebox.showinfo("保存成功", "个人资料已更新", parent=self)

        self._run_request(job, saved)

    def _profile_updated(self, user: dict[str, Any]) -> None:
        if not self.user:
            return
        self.user = user
        self._show_main()
        self._reload_all_lists()

    def _search_messages(self) -> None:
        keyword = simpledialog.askstring("搜索消息", "关键词", parent=self)
        if not keyword:
            return

        def show(response: dict[str, Any]) -> None:
            lines = []
            for msg in response.get("messages", [])[:30]:
                sender = msg.get("sender_group_alias") or msg.get("sender_nickname") or msg.get("sender_username") or "对方"
                lines.append(f"{sender}: {msg.get('content')}")
            messagebox.showinfo("搜索结果", "\n".join(lines) or "没有找到消息")

        self._run_request(lambda: self.client.request("messages.search", keyword=keyword.strip()), show)

    def _logout(self) -> None:
        self._run_request(lambda: self.client.request("logout"), lambda _resp: self._show_login())

    def _reload_all_lists(self) -> None:
        self._reload_friends()
        self._reload_groups()
        self._reload_conversations()
        self._reload_requests()

    def _reload_friends(self) -> None:
        self._run_request(lambda: self.client.request("friends.list"), lambda resp: self._set_friends(resp.get("friends", [])))

    def _reload_groups(self) -> None:
        self._run_request(lambda: self.client.request("groups.list"), lambda resp: self._set_groups(resp.get("groups", [])))

    def _reload_conversations(self) -> None:
        self._run_request(lambda: self.client.request("conversations.list"), lambda resp: self._set_conversations(resp.get("conversations", [])), show_errors=False)

    def _reload_requests(self) -> None:
        self._run_request(lambda: self.client.request("friends.requests.list"), lambda resp: self._set_requests(resp.get("requests", {})), show_errors=False)

    def _set_friends(self, friends: list[dict[str, Any]]) -> None:
        self.friends = friends
        previous_target = self.current_target
        previous_title = self.current_title
        previous_subtitle = self.current_subtitle
        previous_avatar = self.current_avatar_value
        friends_by_id = {int(friend["id"]): friend for friend in friends}
        for target in list(self.chat_windows):
            if target[0] != "direct":
                continue
            if target[1] not in friends_by_id:
                self._close_chat_window(target, clear_target=False)
                continue
            friend = friends_by_id[target[1]]
            view = self.chat_windows.get(target)
            if not view:
                continue
            view["title"] = str(friend.get("remark") or friend.get("nickname") or friend.get("username"))
            view["subtitle"] = "在线" if friend.get("online") else "离线"
            view["avatar_value"] = friend.get("avatar", "")
            self._render_chat_header(target)
        if previous_target and previous_target[0] == "direct" and previous_target[1] not in friends_by_id:
            self.current_target = None
            self.current_title = "请选择会话"
            self.current_subtitle = "从左侧会话、好友或群聊开始"
            self.current_avatar_value = ""
        else:
            self.current_target = previous_target
            self.current_title = previous_title
            self.current_subtitle = previous_subtitle
            self.current_avatar_value = previous_avatar
            if previous_target and previous_target in self.chat_windows:
                self._activate_chat_window(previous_target)
        self._render_list()

    def _set_groups(self, groups: list[dict[str, Any]]) -> None:
        self.groups = groups
        previous_target = self.current_target
        previous_title = self.current_title
        previous_subtitle = self.current_subtitle
        previous_avatar = self.current_avatar_value
        current_group_ids = {int(group["id"]) for group in groups}
        groups_by_id = {int(group["id"]): group for group in groups}
        for target in list(self.chat_windows):
            if target[0] != "group":
                continue
            group_id = target[1]
            if group_id not in current_group_ids:
                self._close_chat_window(target, clear_target=False)
                continue
            group = groups_by_id[group_id]
            view = self.chat_windows.get(target)
            if not view:
                continue
            view["title"] = str(group.get("group_remark") or group.get("name", ""))
            view["subtitle"] = self._group_chat_subtitle(group)
            view["avatar_value"] = group.get("avatar", "")
            self._render_chat_header(target)
        if previous_target and previous_target[0] == "group" and previous_target[1] not in current_group_ids:
            self.current_target = None
            self.current_title = "请选择会话"
            self.current_subtitle = "从左侧会话、好友或群聊开始"
            self.current_avatar_value = ""
        else:
            self.current_target = previous_target
            self.current_title = previous_title
            self.current_subtitle = previous_subtitle
            self.current_avatar_value = previous_avatar
            if previous_target and previous_target in self.chat_windows:
                self._activate_chat_window(previous_target)
        self._render_list()

    def _set_conversations(self, conversations: list[dict[str, Any]]) -> None:
        self.conversations = conversations
        self._render_list()

    def _set_requests(self, requests: dict[str, Any]) -> None:
        self.requests = requests
        self._refresh_nav()
        self._render_list()

    def _handle_event(self, event: dict[str, Any]) -> None:
        action = event.get("action")
        if action in {"presence", "friends.updated"}:
            self._set_friends(event.get("friends", self.friends))
            self._set_conversations(event.get("conversations", self.conversations))
        elif action == "groups.updated":
            self._set_groups(event.get("groups", self.groups))
            self._set_conversations(event.get("conversations", self.conversations))
        elif action == "unread.updated":
            self._set_friends(event.get("friends", self.friends))
            self._set_groups(event.get("groups", self.groups))
            self._set_conversations(event.get("conversations", self.conversations))
        elif action == "requests.updated":
            self._set_requests(event.get("requests", self.requests))
        elif action == "profile.updated":
            self._profile_updated(event["user"])
        elif action == "message.new":
            message = event["message"]
            target = self._target_for_message(message)
            previous_target = self.current_target
            previous_title = self.current_title
            previous_subtitle = self.current_subtitle
            previous_avatar = self.current_avatar_value
            messages, already_present, appended_at_end = self._upsert_message(target, message)
            if self._chat_window_exists(target):
                self._show_current_message_update(target, message, messages, already_present, appended_at_end)
                self._mark_target_read(target)
                self._restore_chat_selection(previous_target, previous_title, previous_subtitle, previous_avatar)
            self._reload_conversations()
        elif action == "message.recalled":
            message = event["message"]
            target = self._target_for_message(message)
            previous_target = self.current_target
            previous_title = self.current_title
            previous_subtitle = self.current_subtitle
            previous_avatar = self.current_avatar_value
            messages = self.messages_by_target.get(target, [])
            for index, old in enumerate(messages):
                if old["id"] == message["id"]:
                    messages[index] = message
                    break
            if self._chat_window_exists(target):
                self._render_messages(messages, target)
                self._restore_chat_selection(previous_target, previous_title, previous_subtitle, previous_avatar)
            self._reload_conversations()
        elif action == "connection.closed":
            messagebox.showwarning("连接断开", event.get("message", "服务器连接已断开"))

    def _mark_target_read(self, target: tuple[str, int]) -> None:
        conversation_type, target_id = target
        self._run_request(
            lambda: self.client.request("messages.read", conversation_type=conversation_type, target_id=target_id),
            lambda _resp: self._reload_conversations(),
            show_errors=False,
        )

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
            merged[int(message["id"])] = message
        return sorted(merged.values(), key=lambda item: (str(item.get("created_at", "")), int(item["id"])))

    def _poll_events(self) -> None:
        for _ in range(10):
            self.client.poll_event(self._handle_event, timeout=0)
        self.after(100, self._poll_events)

    def _run_request(self, func: Callable[[], dict[str, Any]], on_success: Callable[[dict[str, Any]], None], show_errors: bool = True) -> None:
        def worker() -> None:
            try:
                response = func()
            except Exception as exc:
                if show_errors:
                    error_message = str(exc)
                    self.after(0, lambda error_message=error_message: messagebox.showerror("操作失败", error_message))
                return
            self.after(0, lambda response=response: on_success(response))

        threading.Thread(target=worker, daemon=True).start()

    def _on_close(self) -> None:
        self._close_chat_window(clear_target=False)
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
