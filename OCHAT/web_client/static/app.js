const TOKEN_STORAGE_KEY = "ochat_token";
const WEB_SESSION_HEADER = "X-OCHAT-Web-Session";

const state = {
  user: null,
  token: "",
  webSessionId: createWebSessionId(),
  friends: [],
  groups: [],
  conversations: [],
  requests: {},
  messages: new Map(),
  currentTarget: null,
  mode: "chats",
  avatarCache: new Map(),
  fileCache: new Map(),
  markdownCache: new Map(),
  pendingAvatarFile: null,
  pendingAvatarCleared: false,
  pollVersion: 0,
  sidebarCollapsed: false,
  sendingMessage: false,
  messageRenderKey: "",
  messageRenderKeys: [],
  messageRenderFingerprints: new Map(),
  messageTimeCache: new Map(),
  renderAllScheduled: false,
  refreshInFlight: null,
  refreshQueuedShow: false,
};

const emojiList = [
  "😊", "😂", "🤣", "😍", "😘", "😎", "😭", "😡", "👍", "👏", "🙏", "💪", "🎉", "❤️", "🔥", "✨",
  "😀", "😃", "😄", "😁", "😆", "😅", "🙂", "🙃", "😉", "😌", "🤔", "🤨", "😐", "😴", "😇", "🥳",
  "😢", "😤", "😱", "😬", "🤒", "🤕", "🤯", "🥺", "👋", "👌", "✌️", "🤞", "🤟", "🤙", "👊", "✊",
  "🤝", "👀", "🙌", "🫶", "👎", "☝️", "✍️", "💅", "🌹", "🍀", "🍉", "🍔", "🍟", "🍕", "☕", "🍵",
  "🎂", "🎁", "🏆", "🎮", "📚", "💡", "📌", "🚀",
];

const els = {
  authView: document.querySelector("#authView"),
  appView: document.querySelector("#appView"),
  authHint: document.querySelector("#authHint"),
  loginForm: document.querySelector("#loginForm"),
  registerForm: document.querySelector("#registerForm"),
  loginSubmit: document.querySelector("#loginSubmit"),
  registerSubmit: document.querySelector("#registerSubmit"),
  configButton: document.querySelector("#configButton"),
  listTitle: document.querySelector("#listTitle"),
  listSubtitle: document.querySelector("#listSubtitle"),
  itemList: document.querySelector("#itemList"),
  listActions: document.querySelector("#listActions"),
  searchInput: document.querySelector("#searchInput"),
  chatTitle: document.querySelector("#chatTitle"),
  chatSubtitle: document.querySelector("#chatSubtitle"),
  sidebarToggleButton: document.querySelector("#sidebarToggleButton"),
  messages: document.querySelector("#messages"),
  messageInput: document.querySelector("#messageInput"),
  sendButton: document.querySelector("#sendButton"),
  emojiPanel: document.querySelector("#emojiPanel"),
  directProfileButton: document.querySelector("#directProfileButton"),
  editFriendButton: document.querySelector("#editFriendButton"),
  removeFriendButton: document.querySelector("#removeFriendButton"),
  searchMessagesButton: document.querySelector("#searchMessagesButton"),
  downloadFilesButton: document.querySelector("#downloadFilesButton"),
  recallButton: document.querySelector("#recallButton"),
  groupPanelButton: document.querySelector("#groupPanelButton"),
  fileInput: document.querySelector("#fileInput"),
  profileDialog: document.querySelector("#profileDialog"),
  profileForm: document.querySelector("#profileForm"),
  avatarPicker: document.querySelector("#avatarPicker"),
  avatarInput: document.querySelector("#avatarInput"),
  groupDialog: document.querySelector("#groupDialog"),
  groupDialogTitle: document.querySelector("#groupDialogTitle"),
  groupDialogMeta: document.querySelector("#groupDialogMeta"),
  groupActions: document.querySelector("#groupActions"),
  groupMembers: document.querySelector("#groupMembers"),
  userDialog: document.querySelector("#userDialog"),
  userDialogTitle: document.querySelector("#userDialogTitle"),
  userDialogMeta: document.querySelector("#userDialogMeta"),
  userDialogAvatar: document.querySelector("#userDialogAvatar"),
  userDialogRows: document.querySelector("#userDialogRows"),
  searchDialog: document.querySelector("#searchDialog"),
  searchDialogMeta: document.querySelector("#searchDialogMeta"),
  searchResults: document.querySelector("#searchResults"),
  filesDialog: document.querySelector("#filesDialog"),
  filesDialogMeta: document.querySelector("#filesDialogMeta"),
  fileResults: document.querySelector("#fileResults"),
  configDialog: document.querySelector("#configDialog"),
  configForm: document.querySelector("#configForm"),
  toast: document.querySelector("#toast"),
};

function run(fn) {
  return (...args) => Promise.resolve(fn(...args)).catch((error) => showToast(error.message || String(error)));
}

function debounce(fn, delay = 120) {
  let timer = 0;
  return (...args) => {
    window.clearTimeout(timer);
    timer = window.setTimeout(() => fn(...args), delay);
  };
}

function targetKey(target) {
  return target ? `${target.kind}:${target.id}` : "";
}

function createWebSessionId() {
  if (window.crypto?.randomUUID) return window.crypto.randomUUID();
  const bytes = new Uint8Array(16);
  window.crypto?.getRandomValues?.(bytes);
  const random = Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
  return random || `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
}

function requestHeaders(extra = {}) {
  return {
    [WEB_SESSION_HEADER]: state.webSessionId,
    ...extra,
  };
}

async function api(action, payload = {}) {
  const response = await fetch("/api/request", {
    method: "POST",
    headers: requestHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ action, payload }),
  });
  const data = await response.json();
  if (!data.ok) throw new Error(data.message || "请求失败");
  return data;
}

async function fileToBase64(file) {
  const buffer = await file.arrayBuffer();
  let binary = "";
  const bytes = new Uint8Array(buffer);
  for (let index = 0; index < bytes.length; index += 1) binary += String.fromCharCode(bytes[index]);
  return btoa(binary);
}

async function uploadFile(file) {
  return api("files.upload", {
    filename: file.name,
    mime_type: file.type || "application/octet-stream",
    content_b64: await fileToBase64(file),
  });
}

async function loadFile(fileId) {
  const id = Number(fileId);
  if (!id) throw new Error("文件编号无效");
  if (state.fileCache.has(id)) return state.fileCache.get(id);
  const response = await api("files.download", { file_id: id });
  state.fileCache.set(id, response.file);
  return response.file;
}

async function fileDataUrl(fileId) {
  const file = await loadFile(fileId);
  return `data:${file.mime_type || "application/octet-stream"};base64,${file.content_b64}`;
}

function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.remove("hidden");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => els.toast.classList.add("hidden"), 2800);
}

function setAuthHint(message = "", type = "") {
  els.authHint.textContent = message;
  els.authHint.classList.toggle("error", type === "error");
  els.authHint.classList.toggle("success", type === "success");
}

function setAuthLoading(button, loading) {
  button.disabled = loading;
  button.classList.toggle("is-loading", loading);
  button.setAttribute("aria-busy", loading ? "true" : "false");
}

function friendlyAuthError(message, fallback) {
  const text = String(message || "").trim();
  if (!text) return fallback;
  if (text.includes("invalid username or password")) return "账号或密码不正确，请检查后再试。";
  if (text.includes("username already exists")) return "这个用户名已经被使用了，换一个试试。";
  if (text.includes("username must")) return "用户名需要 3-20 位，只能包含字母、数字或下划线。";
  if (text.includes("password must")) return "密码长度需要在 6-64 位之间。";
  if (text.includes("timed out") || text.includes("connection")) return "暂时连接不上服务器，请检查连接设置。";
  return text;
}

function showApp(loginResponse) {
  state.user = loginResponse.user;
  state.token = loginResponse.token || state.token || "";
  state.friends = loginResponse.friends || [];
  state.groups = loginResponse.groups || [];
  state.conversations = loginResponse.conversations || [];
  state.requests = loginResponse.requests || {};
  state.currentTarget = null;
  state.pollVersion += 1;
  if (state.token) sessionStorage.setItem(TOKEN_STORAGE_KEY, state.token);
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  els.appView.classList.remove("chat-open");
  setSidebarCollapsed(false);
  els.authView.classList.add("hidden");
  els.appView.classList.remove("hidden");
  renderAll();
  renderMessages();
  pollEvents(state.pollVersion);
}

function initials(value) {
  return String(value || "O").trim().slice(0, 1).toUpperCase() || "O";
}

async function avatarUrl(avatar) {
  const value = String(avatar || "");
  if (!value.startsWith("file:")) return "";
  if (state.avatarCache.has(value)) return state.avatarCache.get(value);
  const fileId = Number(value.slice(5));
  if (!fileId) return "";
  const url = await fileDataUrl(fileId);
  state.avatarCache.set(value, url);
  return url;
}

function paintAvatar(node, avatar, label) {
  node.textContent = initials(label);
  node.style.backgroundImage = "";
  avatarUrl(avatar)
    .then((url) => {
      if (!url) return;
      node.textContent = "";
      node.style.backgroundImage = `url("${url}")`;
    })
    .catch(() => {});
}

function friendTitle(friend) {
  return friend?.remark || friend?.nickname || friend?.username || "好友";
}

function friendSubtitle(friend) {
  const parts = [];
  parts.push(friend?.online ? "在线" : "离线");
  if (friend?.group_name) parts.push(`分组：${friend.group_name}`);
  if (friend?.signature) parts.push(friend.signature);
  return parts.join(" · ");
}

function groupTitle(group) {
  return group?.group_remark || group?.name || "群聊";
}

function groupSubtitle(group) {
  const parts = [];
  if (group?.group_remark) parts.push(`群名：${group.name}`);
  parts.push(`群身份：${roleLabel(group?.my_role || "member")}`);
  if (group?.my_alias) parts.push(`我的群昵称：${group.my_alias}`);
  return parts.join(" · ");
}

function findFriend(id) {
  return state.friends.find((friend) => Number(friend.id) === Number(id));
}

function findGroup(id) {
  return state.groups.find((group) => Number(group.id) === Number(id));
}

function currentFriend() {
  if (state.currentTarget?.kind !== "direct") return null;
  return findFriend(state.currentTarget.id) || state.currentTarget.friend || null;
}

function currentGroup() {
  if (state.currentTarget?.kind !== "group") return null;
  return findGroup(state.currentTarget.id) || state.currentTarget.group || null;
}

function formatBytes(size) {
  const value = Number(size || 0);
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / 1024 / 1024).toFixed(1)} MB`;
}

function parseMessageTime(value) {
  if (!value) return null;
  const raw = String(value).trim();
  if (state.messageTimeCache.has(raw)) return state.messageTimeCache.get(raw);
  const normalized = raw.replace(" ", "T");
  const parsed = new Date(normalized);
  const result = Number.isNaN(parsed.getTime()) ? null : parsed;
  if (state.messageTimeCache.size > 1200) {
    const firstKey = state.messageTimeCache.keys().next().value;
    if (firstKey !== undefined) state.messageTimeCache.delete(firstKey);
  }
  state.messageTimeCache.set(raw, result);
  return result;
}

function formatMessageTime(value) {
  const parsed = parseMessageTime(value);
  if (!parsed) return String(value || "");
  const pad = (number) => String(number).padStart(2, "0");
  return `${parsed.getFullYear()}-${pad(parsed.getMonth() + 1)}-${pad(parsed.getDate())} ${pad(parsed.getHours())}:${pad(parsed.getMinutes())}`;
}

function shouldShowMessageTime(messages, index) {
  const current = parseMessageTime(messages[index]?.created_at);
  let previous = null;
  for (let cursor = index - 1; cursor >= 0; cursor -= 1) {
    previous = parseMessageTime(messages[cursor]?.created_at);
    if (previous) break;
  }
  return !previous || (current && Math.abs((current.getTime() - previous.getTime()) / 1000) > 120);
}

function messageTimeFlags(messages) {
  const flags = [];
  let previous = null;
  messages.forEach((message, index) => {
    const current = parseMessageTime(message?.created_at);
    flags[index] = Boolean(!previous || (current && Math.abs((current.getTime() - previous.getTime()) / 1000) > 120));
    if (current) previous = current;
  });
  return flags;
}

function isNearMessageBottom() {
  const distance = els.messages.scrollHeight - els.messages.scrollTop - els.messages.clientHeight;
  return distance < 120;
}

function scrollMessagesToLatest({ force = false, settle = false } = {}) {
  if (!force && !isNearMessageBottom()) return;
  const previousBehavior = els.messages.style.scrollBehavior;
  els.messages.style.scrollBehavior = "auto";
  const scrollToBottom = () => {
    els.messages.scrollTop = els.messages.scrollHeight;
  };
  scrollToBottom();
  requestAnimationFrame(() => {
    scrollToBottom();
    requestAnimationFrame(scrollToBottom);
  });
  if (settle) {
    window.setTimeout(scrollToBottom, 80);
    window.setTimeout(scrollToBottom, 180);
  }
  window.setTimeout(() => {
    els.messages.style.scrollBehavior = previousBehavior;
  }, settle ? 220 : 40);
}

function resetMessageRenderState() {
  state.messageRenderKey = "";
  state.messageRenderKeys = [];
  state.messageRenderFingerprints.clear();
}

function setSidebarCollapsed(collapsed) {
  state.sidebarCollapsed = Boolean(collapsed);
  els.appView.classList.toggle("sidebar-collapsed", state.sidebarCollapsed);
  els.sidebarToggleButton?.setAttribute("aria-expanded", state.sidebarCollapsed ? "false" : "true");
}

function toggleSidebar() {
  setSidebarCollapsed(!state.sidebarCollapsed);
}

function shouldCollapseSidebarAfterOpen() {
  return window.matchMedia("(max-width: 700px)").matches;
}

function renderAll() {
  renderNav();
  renderList();
  renderChatHeader();
}

function scheduleRenderAll() {
  if (state.renderAllScheduled) return;
  state.renderAllScheduled = true;
  requestAnimationFrame(() => {
    state.renderAllScheduled = false;
    renderAll();
  });
}

function renderNav() {
  document.querySelectorAll(".rail-button[data-mode]").forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === state.mode);
  });
  paintAvatar(document.querySelector("#profileButton"), state.user?.avatar, state.user?.nickname || state.user?.username);
}

function currentRows() {
  const keyword = els.searchInput.value.trim().toLowerCase();
  let rows = [];
  if (state.mode === "chats") rows = state.conversations;
  if (state.mode === "friends") rows = state.friends;
  if (state.mode === "groups") rows = state.groups;
  if (state.mode === "requests") rows = requestRows();
  if (!keyword) return rows;
  return rows.filter((row) => JSON.stringify(row).toLowerCase().includes(keyword));
}

function requestRows() {
  const friendRequests = state.requests.friend_requests || {};
  const groupInvitations = state.requests.group_invitations || {};
  return [
    ...(friendRequests.incoming || []).map((item) => ({ kind: "friend_request", item })),
    ...(groupInvitations.incoming || []).map((item) => ({ kind: "group_invitation", item })),
    ...(friendRequests.outgoing || []).map((item) => ({ kind: "request_waiting", title: `好友申请：${item.receiver_username}`, subtitle: "等待对方处理" })),
    ...(groupInvitations.outgoing || []).map((item) => ({ kind: "request_waiting", title: `群邀请：${item.group_name}`, subtitle: "等待对方处理" })),
  ];
}

function renderList() {
  const titles = { chats: "消息", friends: "好友", groups: "群聊", requests: "申请" };
  els.listTitle.textContent = titles[state.mode];
  els.listSubtitle.textContent = state.mode === "chats" ? "最近会话" : "快速管理与查看";
  renderActions();
  els.itemList.innerHTML = "";
  const rows = currentRows();
  if (!rows.length) {
    els.itemList.innerHTML = `<div class="item"><div class="item-main"><div class="item-title">暂无内容</div><div class="item-preview">刷新或切换分类看看</div></div></div>`;
    return;
  }
  rows.forEach((row) => els.itemList.appendChild(rowElement(row)));
}

function renderActions() {
  els.listActions.innerHTML = "";
  const actions = [["刷新", refreshAll]];
  if (state.mode === "chats") {
    actions.unshift(["加好友", addFriend], ["建群", createGroup]);
    actions.push(["查用户", searchUsers], ["搜消息", searchMessages]);
  } else if (state.mode === "friends") {
    actions.unshift(["加好友", addFriend]);
    actions.push(["查用户", searchUsers], ["改备注", () => editFriend(currentFriend())], ["删除", () => removeFriend(currentFriend())]);
  } else if (state.mode === "groups") {
    actions.unshift(["建群", createGroup]);
    actions.push(["邀请", () => inviteMember(currentGroup()?.id)], ["群面板", openGroupPanel]);
  } else {
    actions.unshift(["加好友", addFriend]);
    actions.push(["查用户", searchUsers]);
  }
  actions.forEach(([text, fn]) => {
    const button = document.createElement("button");
    button.className = text === "删除" ? "soft danger-action" : "soft";
    button.textContent = text;
    button.onclick = run(fn);
    els.listActions.appendChild(button);
  });
}

function rowElement(row) {
  const button = document.createElement("button");
  button.className = "item";
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  const main = document.createElement("div");
  main.className = "item-main";
  const meta = document.createElement("div");
  meta.className = "item-meta";
  let title = "";
  let subtitle = "";
  let avatarValue = "";
  let unread = 0;

  if (state.mode === "chats") {
    title = row.title;
    subtitle = row.preview || "暂无消息";
    meta.textContent = row.subtitle || "";
    avatarValue = row.peer?.avatar || "";
    unread = Number(row.unread_count || 0);
    if (row.conversation_type === "group") avatarValue = "";
    button.classList.toggle("active", targetKey(state.currentTarget) === `${row.conversation_type}:${row.target_id}`);
    button.onclick = run(() => openConversation(row));
  } else if (state.mode === "friends") {
    title = friendTitle(row);
    subtitle = row.signature || row.username;
    meta.textContent = row.online ? "在线" : "离线";
    avatarValue = row.avatar || "";
    unread = Number(row.unread_count || 0);
    button.classList.toggle("active", targetKey(state.currentTarget) === `direct:${row.id}`);
    button.onclick = run(() => openDirect(row));
  } else if (state.mode === "groups") {
    title = groupTitle(row);
    subtitle = groupSubtitle(row);
    meta.textContent = "群聊";
    unread = Number(row.unread_count || 0);
    button.classList.toggle("active", targetKey(state.currentTarget) === `group:${row.id}`);
    button.onclick = run(() => openGroup(row));
  } else {
    return requestElement(row);
  }

  paintAvatar(avatar, avatarValue, title);
  main.innerHTML = `<div class="item-title"></div><div class="item-preview"></div>`;
  main.querySelector(".item-title").textContent = title;
  main.querySelector(".item-preview").textContent = subtitle;
  button.append(avatar, main, meta);
  if (unread > 0) {
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = String(Math.min(unread, 99));
    button.appendChild(badge);
  }
  return button;
}

function requestElement(row) {
  const box = document.createElement("div");
  box.className = "item";
  const main = document.createElement("div");
  main.className = "item-main";
  const item = row.item || {};
  let title = row.title || "";
  let subtitle = row.subtitle || "";
  if (row.kind === "friend_request") {
    title = `好友申请：${item.requester_nickname || item.requester_username}`;
    subtitle = item.message || "请求添加你为好友";
  }
  if (row.kind === "group_invitation") {
    title = `群邀请：${item.group_name}`;
    subtitle = item.message || `${item.inviter_username} 邀请你加入群聊`;
  }
  main.innerHTML = `<div class="item-title"></div><div class="item-preview"></div>`;
  main.querySelector(".item-title").textContent = title;
  main.querySelector(".item-preview").textContent = subtitle;
  const actions = document.createElement("div");
  if (row.kind === "friend_request" || row.kind === "group_invitation") {
    const accept = document.createElement("button");
    accept.className = "soft";
    accept.textContent = "同意";
    accept.onclick = run(() => respondRequest(row, true));
    const reject = document.createElement("button");
    reject.className = "soft";
    reject.textContent = "拒绝";
    reject.onclick = run(() => respondRequest(row, false));
    actions.append(accept, reject);
  }
  box.append(main, actions);
  return box;
}

async function openConversation(row) {
  if (row.conversation_type === "direct") {
    const friend = row.peer || findFriend(row.target_id) || {};
    state.currentTarget = {
      kind: "direct",
      id: Number(row.target_id),
      title: row.title || friendTitle(friend),
      subtitle: row.subtitle || friendSubtitle(friend),
      friend,
    };
    const response = await api("messages.direct.history", { friend_id: row.target_id });
    state.messages.set(targetKey(state.currentTarget), response.messages || []);
  } else {
    const group = row.group || findGroup(row.target_id) || {};
    state.currentTarget = {
      kind: "group",
      id: Number(row.target_id),
      title: row.title || groupTitle(group),
      subtitle: row.subtitle || groupSubtitle(group),
      group,
    };
    const response = await api("messages.group.history", { group_id: row.target_id });
    state.messages.set(targetKey(state.currentTarget), response.messages || []);
  }
  els.appView.classList.add("chat-open");
  if (shouldCollapseSidebarAfterOpen()) setSidebarCollapsed(true);
  renderAll();
  renderMessages({ forceScroll: true, settleScroll: true });
}

function openDirect(friend) {
  return openConversation({
    conversation_type: "direct",
    target_id: friend.id,
    title: friendTitle(friend),
    subtitle: friendSubtitle(friend),
    peer: friend,
  });
}

function openGroup(group) {
  return openConversation({
    conversation_type: "group",
    target_id: group.id,
    title: groupTitle(group),
    subtitle: groupSubtitle(group),
    group,
  });
}

async function openTarget(target) {
  const conversation = state.conversations.find(
    (item) => item.conversation_type === target.kind && Number(item.target_id) === Number(target.id),
  );
  if (conversation) return openConversation(conversation);
  if (target.kind === "direct") {
    const friend = findFriend(target.id);
    if (!friend) throw new Error("找不到该好友会话");
    return openDirect(friend);
  }
  const group = findGroup(target.id);
  if (!group) throw new Error("找不到该群聊会话");
  return openGroup(group);
}

function renderChatHeader() {
  const friend = currentFriend();
  const group = currentGroup();
  if (friend && state.currentTarget) {
    state.currentTarget.title = friendTitle(friend);
    state.currentTarget.subtitle = friendSubtitle(friend);
    state.currentTarget.friend = friend;
  }
  if (group && state.currentTarget) {
    state.currentTarget.title = groupTitle(group);
    state.currentTarget.subtitle = groupSubtitle(group);
    state.currentTarget.group = group;
  }
  els.chatTitle.textContent = state.currentTarget?.title || "请选择会话";
  els.chatSubtitle.textContent = state.currentTarget?.subtitle || "从左侧选择好友或群聊开始";
  const hasTarget = Boolean(state.currentTarget);
  const isDirect = state.currentTarget?.kind === "direct";
  const isGroup = state.currentTarget?.kind === "group";
  els.directProfileButton.classList.toggle("hidden", !isDirect);
  els.editFriendButton.classList.toggle("hidden", !isDirect);
  els.removeFriendButton.classList.toggle("hidden", !isDirect);
  els.groupPanelButton.classList.toggle("hidden", !isGroup);
  els.searchMessagesButton.classList.toggle("hidden", !hasTarget);
  els.downloadFilesButton.classList.toggle("hidden", !hasTarget);
  els.recallButton.classList.toggle("hidden", !hasTarget);
}

function renderMessages({ incremental = false, forceScroll = true, settleScroll = false } = {}) {
  els.appView.classList.toggle("chat-open", Boolean(state.currentTarget));
  const key = targetKey(state.currentTarget);
  const rows = state.messages.get(key) || [];
  els.messages.classList.toggle("empty", !rows.length);
  if (!state.currentTarget) {
    resetMessageRenderState();
    els.messages.textContent = "请选择一个会话开始聊天";
    return;
  }
  if (!rows.length) {
    resetMessageRenderState();
    els.messages.textContent = "暂无消息";
    return;
  }
  if (incremental && state.messageRenderKey === key && syncRenderedMessages(rows)) {
    scrollMessagesToLatest({ force: forceScroll, settle: settleScroll });
    return;
  }
  const fragment = document.createDocumentFragment();
  const timeFlags = messageTimeFlags(rows);
  rows.forEach((message, index) => fragment.appendChild(messageElement(message, timeFlags[index])));
  els.messages.replaceChildren(fragment);
  rememberRenderedMessages(key, rows, timeFlags);
  scrollMessagesToLatest({ force: forceScroll, settle: settleScroll });
}

function messageElement(message, showTime = true) {
  const mine = Number(message.sender_id) === Number(state.user.id);
  const displayName = mine ? "我" : message.sender_group_alias || message.sender_nickname || message.sender_username || "对方";
  const item = document.createElement("article");
  item.className = `message ${mine ? "mine" : ""}`;
  item.dataset.messageKey = messageDomKey(message);
  item.dataset.messageFingerprint = messageFingerprint(message, showTime);

  const avatar = document.createElement("div");
  avatar.className = "avatar message-avatar";
  paintAvatar(avatar, mine ? state.user?.avatar : message.sender_avatar, displayName);
  if (!mine) avatar.onclick = () => showMessageSenderProfile(message);

  const body = document.createElement("div");
  body.className = "message-body";
  if (!mine) {
    const meta = document.createElement("div");
    meta.className = "message-meta";
    meta.textContent = displayName;
    body.appendChild(meta);
  }
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  renderBubbleContent(bubble, message);
  body.appendChild(bubble);

  const footerParts = [];
  if (showTime && message.created_at) footerParts.push(formatMessageTime(message.created_at));
  if (message.status === "recalled") footerParts.push("已撤回");
  if (footerParts.length) {
    const footer = document.createElement("div");
    footer.className = "message-footer";
    footer.textContent = footerParts.join(" · ");
    body.appendChild(footer);
  }

  const actions = document.createElement("div");
  actions.className = "message-actions";
  if (message.file_id && message.status !== "recalled") {
    const download = document.createElement("button");
    download.textContent = "下载";
    download.onclick = run(() => downloadFileMessage(message));
    actions.appendChild(download);
  }
  if (mine && message.status !== "recalled") {
    const recall = document.createElement("button");
    recall.textContent = "撤回";
    recall.onclick = run(() => recallMessage(message.id));
    actions.appendChild(recall);
  }
  if (actions.children.length) body.appendChild(actions);

  if (mine) item.append(body, avatar);
  else item.append(avatar, body);
  return item;
}

function syncRenderedMessages(rows) {
  const renderedKeys = state.messageRenderKeys;
  const renderedCount = renderedKeys.length;
  const domCount = els.messages.childElementCount;
  if (!renderedCount || renderedCount !== domCount) return false;

  if (renderedCount === rows.length - 1) {
    const previousKey = messageDomKey(rows[renderedCount - 1]);
    if (renderedKeys[renderedCount - 1] !== previousKey) return false;
    appendRenderedMessage(rows, renderedCount);
    return true;
  }

  if (renderedCount !== rows.length) return false;

  for (let index = 0; index < rows.length; index += 1) {
    const message = rows[index];
    const key = messageDomKey(message);
    if (renderedKeys[index] !== key) return false;
    const showTime = shouldShowMessageTime(rows, index);
    const fingerprint = messageFingerprint(message, showTime);
    if (state.messageRenderFingerprints.get(key) === fingerprint) continue;
    const node = els.messages.children[index];
    if (!node) return false;
    node.replaceWith(messageElement(message, showTime));
    state.messageRenderFingerprints.set(key, fingerprint);
  }
  return true;
}

function appendRenderedMessage(rows, index) {
  const message = rows[index];
  const showTime = shouldShowMessageTime(rows, index);
  const key = messageDomKey(message);
  els.messages.appendChild(messageElement(message, showTime));
  state.messageRenderKeys.push(key);
  state.messageRenderFingerprints.set(key, messageFingerprint(message, showTime));
}

function rememberRenderedMessages(key, rows, timeFlags) {
  state.messageRenderKey = key;
  state.messageRenderKeys = [];
  state.messageRenderFingerprints.clear();
  rows.forEach((message, index) => {
    const messageKey = messageDomKey(message);
    state.messageRenderKeys.push(messageKey);
    state.messageRenderFingerprints.set(messageKey, messageFingerprint(message, timeFlags[index]));
  });
}

function messageDomKey(message) {
  if (message?.id !== undefined && message?.id !== null) return `message:${message.id}`;
  return [
    "transient",
    message?.conversation_type || "",
    message?.sender_id || "",
    message?.target_id || "",
    message?.created_at || "",
    message?.message_type || "",
    message?.content || "",
  ].join(":");
}

function messageFingerprint(message, showTime) {
  return [
    message?.status || "",
    message?.content || "",
    message?.message_type || "",
    message?.file_id || "",
    message?.file_name || "",
    message?.file_size || "",
    message?.sender_avatar || "",
    message?.sender_group_alias || "",
    message?.sender_nickname || "",
    message?.sender_username || "",
    message?.created_at || "",
    showTime ? "time" : "no-time",
  ].join("\u001f");
}

function renderBubbleContent(bubble, message) {
  if (message.status === "recalled") {
    bubble.textContent = "消息已撤回";
    return;
  }
  if (message.message_type === "image" && message.file_id) {
    const image = document.createElement("img");
    image.className = "image-preview";
    image.alt = message.file_name || "图片";
    image.src = "";
    image.loading = "lazy";
    image.decoding = "async";
    const placeholder = document.createElement("div");
    placeholder.className = "file-meta";
    placeholder.textContent = "图片加载中...";
    fileDataUrl(message.file_id)
      .then((url) => {
        image.src = url;
        placeholder.remove();
      })
      .catch(() => {
        placeholder.textContent = "图片加载失败，仍可下载文件";
      });
    bubble.append(image, placeholder, fileSummary(message));
    return;
  }
  if (message.message_type === "file" && message.file_id) {
    bubble.appendChild(fileSummary(message));
    return;
  }
  renderTextContent(bubble, message.content || "");
}

function renderTextContent(container, content) {
  const text = String(content || "");
  const cached = state.markdownCache.get(text);
  if (cached) {
    container.appendChild(cached.cloneNode(true));
    return;
  }
  const markdown = document.createElement("div");
  markdown.className = "message-markdown";
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];
    if (!line.trim()) {
      index += 1;
      continue;
    }

    if (/^```/.test(line.trim())) {
      const language = line.trim().slice(3).trim();
      const codeLines = [];
      index += 1;
      while (index < lines.length && !/^```/.test(lines[index].trim())) {
        codeLines.push(lines[index]);
        index += 1;
      }
      if (index < lines.length) index += 1;
      const pre = document.createElement("pre");
      const code = document.createElement("code");
      if (language) code.dataset.language = language;
      code.textContent = codeLines.join("\n");
      pre.appendChild(code);
      markdown.appendChild(pre);
      continue;
    }

    if (/^>\s?/.test(line)) {
      const quoteLines = [];
      while (index < lines.length && /^>\s?/.test(lines[index])) {
        quoteLines.push(lines[index].replace(/^>\s?/, ""));
        index += 1;
      }
      const quote = document.createElement("blockquote");
      appendInlineWithBreaks(quote, quoteLines.join("\n"));
      markdown.appendChild(quote);
      continue;
    }

    if (/^\s*[-*]\s+/.test(line)) {
      const list = document.createElement("ul");
      while (index < lines.length && /^\s*[-*]\s+/.test(lines[index])) {
        const item = document.createElement("li");
        appendInlineText(item, lines[index].replace(/^\s*[-*]\s+/, ""));
        list.appendChild(item);
        index += 1;
      }
      markdown.appendChild(list);
      continue;
    }

    if (/^\s*\d+\.\s+/.test(line)) {
      const list = document.createElement("ol");
      while (index < lines.length && /^\s*\d+\.\s+/.test(lines[index])) {
        const item = document.createElement("li");
        appendInlineText(item, lines[index].replace(/^\s*\d+\.\s+/, ""));
        list.appendChild(item);
        index += 1;
      }
      markdown.appendChild(list);
      continue;
    }

    const paragraphLines = [];
    while (index < lines.length && lines[index].trim() && !isMarkdownBlockStart(lines[index])) {
      paragraphLines.push(lines[index]);
      index += 1;
    }
    appendParagraph(markdown, paragraphLines.join("\n"));
  }

  if (!markdown.childElementCount) markdown.textContent = text;
  rememberMarkdown(text, markdown);
  container.appendChild(markdown);
}

function rememberMarkdown(content, node) {
  if (state.markdownCache.size > 220) {
    const firstKey = state.markdownCache.keys().next().value;
    if (firstKey !== undefined) state.markdownCache.delete(firstKey);
  }
  state.markdownCache.set(content, node.cloneNode(true));
}

function isMarkdownBlockStart(line) {
  return /^```/.test(line.trim()) || /^>\s?/.test(line) || /^\s*[-*]\s+/.test(line) || /^\s*\d+\.\s+/.test(line);
}

function appendParagraph(container, text) {
  const paragraph = document.createElement("p");
  appendInlineWithBreaks(paragraph, text);
  container.appendChild(paragraph);
}

function appendInlineWithBreaks(parent, text) {
  String(text || "")
    .split("\n")
    .forEach((line, index) => {
      if (index) parent.appendChild(document.createElement("br"));
      appendInlineText(parent, line);
    });
}

function appendInlineText(parent, text) {
  String(text || "")
    .split(/(`[^`\n]+`)/g)
    .forEach((part) => {
      if (!part) return;
      if (part.startsWith("`") && part.endsWith("`") && part.length > 1) {
        const code = document.createElement("code");
        code.textContent = part.slice(1, -1);
        parent.appendChild(code);
        return;
      }
      parent.appendChild(document.createTextNode(part));
    });
}

function fileSummary(message) {
  const card = document.createElement("div");
  card.className = "file-card";
  const title = document.createElement("div");
  title.className = "file-title";
  title.textContent = message.file_name || `ochat_file_${message.file_id}`;
  const meta = document.createElement("div");
  meta.className = "file-meta";
  meta.textContent = `${message.message_type === "image" ? "图片" : "文件"} · ${formatBytes(message.file_size)} · ${message.content || ""}`;
  const button = document.createElement("button");
  button.className = "file-download";
  button.textContent = "下载文件";
  button.onclick = run(() => downloadFileMessage(message));
  card.append(title, meta, button);
  return card;
}

async function sendMessage() {
  const content = els.messageInput.value.trim();
  if (!state.currentTarget || !content || state.sendingMessage) return;
  state.sendingMessage = true;
  els.sendButton.disabled = true;
  els.sendButton.classList.add("is-sending");
  els.messageInput.value = "";
  try {
    const response =
      state.currentTarget.kind === "direct"
        ? await api("messages.direct.send", { receiver_id: state.currentTarget.id, content })
        : await api("messages.group.send", { group_id: state.currentTarget.id, content });
    applySentMessage(response);
  } finally {
    state.sendingMessage = false;
    els.sendButton.disabled = false;
    els.sendButton.classList.remove("is-sending");
  }
}

async function sendPickedFile(file) {
  if (!state.currentTarget || !file) return;
  const upload = await uploadFile(file);
  const fileId = upload.file.id;
  const image = /\.(png|jpg|jpeg|gif)$/i.test(file.name);
  const payload = { content: `已发送 ${file.name}`, message_type: image ? "image" : "file", file_id: fileId };
  const response =
    state.currentTarget.kind === "direct"
      ? await api("messages.direct.send", { ...payload, receiver_id: state.currentTarget.id })
      : await api("messages.group.send", { ...payload, group_id: state.currentTarget.id });
  applySentMessage(response);
  els.fileInput.value = "";
}

function applySentMessage(response) {
  const message = response?.message;
  if (!message || typeof message !== "object") {
    scrollMessagesToLatest();
    return;
  }
  const target = messageTarget(message);
  const key = targetKey(target);
  const rows = state.messages.get(key) || [];
  state.messages.set(key, mergeMessages(rows, [message]));
  if (key === targetKey(state.currentTarget)) renderMessages({ incremental: true, forceScroll: true, settleScroll: true });
}

async function refreshAll(show = true) {
  if (state.refreshInFlight) {
    state.refreshQueuedShow = state.refreshQueuedShow || show;
    return state.refreshInFlight;
  }
  state.refreshInFlight = refreshState(show);
  try {
    return await state.refreshInFlight;
  } finally {
    state.refreshInFlight = null;
    if (state.refreshQueuedShow) {
      state.refreshQueuedShow = false;
      refreshAll(true);
    }
  }
}

async function refreshState(show = true) {
  try {
    const response = await loadStateSnapshot();
    state.friends = response.friends || [];
    state.groups = response.groups || [];
    state.conversations = response.conversations || [];
    state.requests = response.requests || {};
    renderAll();
    if (show) showToast("已刷新");
  } catch (error) {
    if (show) showToast(error.message);
  }
}

async function loadStateSnapshot() {
  try {
    return await api("bridge.state");
  } catch {
    const [friends, groups, conversations, requests] = await Promise.all([
      api("friends.list"),
      api("groups.list"),
      api("conversations.list"),
      api("friends.requests.list"),
    ]);
    return {
      friends: friends.friends || [],
      groups: groups.groups || [],
      conversations: conversations.conversations || [],
      requests: requests.requests || {},
    };
  }
}

async function pollEvents(version) {
  while (state.user && state.pollVersion === version) {
    try {
      const response = await fetch("/api/events?timeout=20", { headers: requestHeaders() });
      const data = await response.json();
      if (!state.user || state.pollVersion !== version) break;
      if (data.ok && data.event) handleEvent(data.event);
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 1200));
    }
  }
}

function handleEvent(event) {
  let shouldRenderAll = false;
  if (event.friends) {
    state.friends = event.friends;
    shouldRenderAll = true;
  }
  if (event.groups) {
    state.groups = event.groups;
    shouldRenderAll = true;
  }
  if (event.conversations) {
    state.conversations = event.conversations;
    shouldRenderAll = true;
  }
  if (event.requests) {
    state.requests = event.requests;
    shouldRenderAll = true;
  }
  if (event.user) {
    state.user = event.user;
    shouldRenderAll = true;
  }
  if (event.action === "message.new" || event.action === "message.recalled") {
    const target = messageTarget(event.message);
    const key = targetKey(target);
    const rows = state.messages.get(key) || [];
    const shouldStickToBottom = key === targetKey(state.currentTarget) && isNearMessageBottom();
    state.messages.set(key, mergeMessages(rows, [event.message]));
    if (key === targetKey(state.currentTarget)) {
      renderMessages({ incremental: true, forceScroll: shouldStickToBottom, settleScroll: shouldStickToBottom });
    }
  }
  if (shouldRenderAll) scheduleRenderAll();
}

function messageTarget(message) {
  if (message.conversation_type === "group") return { kind: "group", id: Number(message.target_id) };
  const other = Number(message.sender_id) === Number(state.user.id) ? Number(message.target_id) : Number(message.sender_id);
  return { kind: "direct", id: other };
}

function mergeMessages(existing, incoming) {
  if (!incoming.length) return existing;
  if (!existing.length) return incoming.slice().sort(compareMessages);

  if (incoming.length === 1 && canAppendMessage(existing, incoming[0])) {
    return [...existing, incoming[0]];
  }

  const merged = existing.slice();
  const indexByKey = new Map();
  merged.forEach((item, index) => indexByKey.set(messageIdentityKey(item), index));
  let needsSort = false;

  incoming.forEach((item) => {
    const key = messageIdentityKey(item);
    const index = indexByKey.get(key);
    if (index !== undefined) {
      merged[index] = item;
      return;
    }
    if (merged.length && compareMessages(merged[merged.length - 1], item) > 0) needsSort = true;
    indexByKey.set(key, merged.length);
    merged.push(item);
  });

  if (needsSort) merged.sort(compareMessages);
  return merged;
}

function canAppendMessage(existing, message) {
  const last = existing[existing.length - 1];
  if (!last) return true;
  const messageId = Number(message?.id);
  const lastId = Number(last?.id);
  if (Number.isFinite(messageId) && Number.isFinite(lastId) && messageId <= lastId) return false;
  return compareMessages(last, message) <= 0;
}

function compareMessages(a, b) {
  return String(a?.created_at || "").localeCompare(String(b?.created_at || "")) || Number(a?.id || 0) - Number(b?.id || 0);
}

function messageIdentityKey(message) {
  const id = Number(message?.id);
  return Number.isFinite(id) ? `id:${id}` : messageDomKey(message);
}

async function addFriend() {
  const username = prompt("请输入对方用户名");
  if (!username) return;
  const message = prompt("验证消息（可留空）") || "";
  await api("friends.request", { username: username.trim(), message });
  showToast("好友申请已发送");
  refreshAll(false);
}

async function searchUsers() {
  const keyword = prompt("请输入用户名或昵称关键词");
  if (!keyword) return;
  const response = await api("users.search", { keyword: keyword.trim() });
  showUserSearchResults(response.users || []);
}

function showUserSearchResults(users) {
  els.searchDialogMeta.textContent = users.length ? `找到 ${users.length} 个用户，点击可发送好友申请` : "没有找到用户";
  els.searchResults.innerHTML = "";
  users.forEach((user) => {
    const button = document.createElement("button");
    button.className = "result-item";
    button.innerHTML = `<div class="result-title"></div><div class="result-meta"></div><div class="result-preview"></div>`;
    button.querySelector(".result-title").textContent = user.nickname || user.username;
    button.querySelector(".result-meta").textContent = `用户名：${user.username}`;
    button.querySelector(".result-preview").textContent = user.signature || "未填写签名";
    button.onclick = run(async () => {
      const ok = confirm(`向 ${user.username} 发送好友申请？`);
      if (!ok) return;
      const message = prompt("验证消息（可留空）") || "";
      await api("friends.request", { username: user.username, message });
      showToast("好友申请已发送");
      els.searchDialog.close();
    });
    els.searchResults.appendChild(button);
  });
  if (!users.length) els.searchResults.innerHTML = `<div class="result-item"><div class="result-title">没有找到用户</div></div>`;
  if (!els.searchDialog.open) els.searchDialog.showModal();
}

async function createGroup() {
  const name = prompt("群聊名称");
  if (!name) return;
  await api("groups.create", { name: name.trim() });
  refreshAll();
}

async function respondRequest(row, accept) {
  if (row.kind === "friend_request") {
    const payload = { friend_request_id: row.item.id, accept };
    if (accept) {
      payload.remark = prompt("好友备注（可留空）") || "";
      payload.group_name = prompt("好友分组", "Friends") || "Friends";
    }
    await api("friends.requests.respond", payload);
  }
  if (row.kind === "group_invitation") await api("groups.invitations.respond", { invitation_id: row.item.id, accept });
  refreshAll();
}

function roleLabel(role) {
  return { owner: "群主", admin: "管理员", member: "成员" }[role] || role || "成员";
}

async function openGroupPanel() {
  if (state.currentTarget?.kind !== "group") {
    showToast("请先选择一个群聊");
    return;
  }
  const response = await api("groups.members", { group_id: state.currentTarget.id });
  const localGroup = findGroup(state.currentTarget.id) || state.currentTarget.group || {};
  const group = {
    id: state.currentTarget.id,
    name: localGroup.name || state.currentTarget.title || "群聊",
    my_role: localGroup.my_role || "member",
    ...localGroup,
    ...(response.group || {}),
  };
  state.currentTarget.group = group;
  state.currentTarget.title = groupTitle(group);
  state.currentTarget.subtitle = groupSubtitle(group);
  const members = response.members || [];
  const myMember = members.find((member) => Number(member.id) === Number(state.user.id)) || { id: state.user.id, alias: "" };
  els.groupDialogTitle.textContent = groupTitle(group);
  els.groupDialogMeta.textContent = `${members.length} 人 · 我的身份：${roleLabel(group.my_role)}`;
  els.groupActions.innerHTML = "";
  if (["owner", "admin"].includes(group.my_role)) addGroupAction("邀请成员", () => inviteMember(group.id));
  if (["owner", "admin"].includes(group.my_role)) addGroupAction("修改群名", () => renameGroup(group.id, group.name));
  addGroupAction("搜索消息", searchMessages);
  addGroupAction("我的群昵称", () => updateGroupMemberAlias(group.id, myMember));
  addGroupAction("修改备注", () => updateGroupRemark(group.id, group));
  addGroupAction("刷新", () => openGroupPanel());
  addGroupAction("退出群聊", () => leaveGroup(group.id, group.my_role));
  if (group.my_role === "owner") addGroupAction("解散群聊", () => dismissGroup(group.id), true);
  els.groupMembers.innerHTML = "";
  members.forEach((member) => els.groupMembers.appendChild(memberElement(group, member)));
  renderChatHeader();
  if (!els.groupDialog.open) els.groupDialog.showModal();
}

function addGroupAction(text, fn, danger = false) {
  const button = document.createElement("button");
  button.className = danger ? "soft danger-action" : "soft";
  button.textContent = text;
  button.onclick = run(fn);
  els.groupActions.appendChild(button);
}

function memberElement(group, member) {
  const row = document.createElement("div");
  row.className = "member";
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  const name = member.alias || member.nickname || member.username;
  paintAvatar(avatar, member.avatar, name);
  avatar.onclick = () => showUserProfile(member, "成员资料");
  const main = document.createElement("div");
  main.className = "item-main";
  main.innerHTML = `<div class="item-title"></div><div class="item-preview"></div>`;
  main.querySelector(".item-title").textContent = name;
  const metaParts = [`${member.username} · ${roleLabel(member.role)}`];
  if (member.alias) metaParts.push(`原昵称：${member.nickname || member.username}`);
  if (Number(member.id) === Number(state.user.id)) metaParts.push("我");
  main.querySelector(".item-preview").textContent = metaParts.join(" · ");
  const tools = document.createElement("div");
  tools.className = "member-tools";
  const mine = Number(member.id) === Number(state.user.id);
  const profile = document.createElement("button");
  profile.className = "soft";
  profile.textContent = "资料";
  profile.onclick = () => showUserProfile(member, "成员资料");
  tools.appendChild(profile);
  if (mine || ["owner", "admin"].includes(group.my_role)) {
    const alias = document.createElement("button");
    alias.className = "soft";
    alias.textContent = mine ? "我的群昵称" : "群昵称";
    alias.onclick = run(() => updateGroupMemberAlias(group.id, member));
    tools.appendChild(alias);
  }
  if (!mine && group.my_role === "owner" && member.role !== "owner") {
    const roleButton = document.createElement("button");
    roleButton.className = "soft";
    roleButton.textContent = member.role === "admin" ? "取消管理员" : "设为管理员";
    roleButton.onclick = run(() => setMemberRole(group.id, member.id, member.role === "admin" ? "member" : "admin"));
    tools.appendChild(roleButton);
  }
  if (!mine && (group.my_role === "owner" || (group.my_role === "admin" && member.role === "member"))) {
    const remove = document.createElement("button");
    remove.className = "soft danger-action";
    remove.textContent = "移出";
    remove.onclick = run(() => removeMember(group.id, member.id, name));
    tools.appendChild(remove);
  }
  row.append(avatar, main, tools);
  return row;
}

async function inviteMember(groupId) {
  const id = groupId || currentGroup()?.id;
  if (!id) {
    showToast("请先选择一个群聊");
    return;
  }
  const username = prompt("请输入用户名");
  if (!username) return;
  const message = prompt("邀请消息（可留空）") || "";
  await api("groups.invite.request", { group_id: id, username: username.trim(), message });
  showToast("群邀请已发送");
  refreshAll(false);
}

async function renameGroup(groupId, oldName) {
  const name = prompt("群聊名称", oldName || "");
  if (!name) return;
  await api("groups.rename", { group_id: groupId, name: name.trim() });
  await refreshAll(false);
  await openGroupPanel();
}

async function updateGroupRemark(groupId, group) {
  const groupRemark = prompt("群备注（只对自己显示，可留空）", group?.group_remark || "");
  if (groupRemark === null) return;
  await api("groups.remark.update", { group_id: groupId, group_remark: groupRemark.trim() });
  await refreshAll(false);
  await openGroupPanel();
}

async function updateGroupMemberAlias(groupId, member) {
  if (!member) return;
  const alias = prompt("群昵称（可留空）", member.alias || "");
  if (alias === null) return;
  await api("groups.member_alias.update", { group_id: groupId, member_id: member.id, alias: alias.trim() });
  await openGroupPanel();
}

async function setMemberRole(groupId, memberId, role) {
  await api("groups.member_role.update", { group_id: groupId, member_id: memberId, role });
  await openGroupPanel();
}

async function removeMember(groupId, memberId, name) {
  if (!confirm(`确认将 ${name} 移出群聊？`)) return;
  await api("groups.remove_member", { group_id: groupId, member_id: memberId });
  await openGroupPanel();
}

async function leaveGroup(groupId, myRole) {
  const text = myRole === "owner" ? "你是群主，退出后会自动转让群主。确认退出？" : "确认退出该群聊？";
  if (!confirm(text)) return;
  await api("groups.leave", { group_id: groupId });
  els.groupDialog.close();
  state.currentTarget = null;
  els.appView.classList.remove("chat-open");
  await refreshAll(false);
  renderMessages();
}

async function dismissGroup(groupId) {
  if (!confirm("确认解散该群聊？")) return;
  await api("groups.dismiss", { group_id: groupId });
  els.groupDialog.close();
  state.currentTarget = null;
  els.appView.classList.remove("chat-open");
  await refreshAll(false);
  renderMessages();
}

function showDirectProfile() {
  const friend = currentFriend();
  if (!friend) {
    showToast("请先选择一个好友");
    return;
  }
  showUserProfile(friend, "好友资料");
}

function showMessageSenderProfile(message) {
  const senderId = Number(message.sender_id || 0);
  if (!senderId || senderId === Number(state.user.id)) return;
  const profile =
    findFriend(senderId) || {
      id: senderId,
      username: message.sender_username || "",
      nickname: message.sender_group_alias || message.sender_nickname || "",
      avatar: message.sender_avatar || "",
    };
  showUserProfile(profile, "个人资料");
}

function showUserProfile(profile, title = "个人资料") {
  const name = profile.alias || profile.remark || profile.nickname || profile.username || "用户";
  els.userDialogTitle.textContent = title;
  els.userDialogMeta.textContent = profile.username ? `用户名：${profile.username}` : "";
  paintAvatar(els.userDialogAvatar, profile.avatar, name);
  els.userDialogRows.innerHTML = "";
  [
    ["昵称", profile.nickname],
    ["备注", profile.remark],
    ["分组", profile.group_name],
    ["群昵称", profile.alias],
    ["身份", profile.role ? roleLabel(profile.role) : ""],
    ["性别", profile.gender],
    ["生日", profile.birthday],
    ["年龄", profile.age],
    ["联系方式", profile.contact],
    ["住址", profile.address],
    ["签名", profile.signature],
  ].forEach(([label, value]) => addDetailRow(els.userDialogRows, label, value));
  if (!els.userDialog.open) els.userDialog.showModal();
}

function addDetailRow(parent, label, value) {
  const row = document.createElement("div");
  row.className = "detail-row";
  const key = document.createElement("div");
  key.className = "detail-label";
  key.textContent = label;
  const val = document.createElement("div");
  val.className = "detail-value";
  val.textContent = value === null || value === undefined || String(value).trim() === "" ? "未填写" : String(value);
  row.append(key, val);
  parent.appendChild(row);
}

async function editFriend(friend) {
  if (!friend) {
    showToast("请先选择一个好友");
    return;
  }
  const remark = prompt("备注", friend.remark || "");
  if (remark === null) return;
  const groupName = prompt("好友分组", friend.group_name || "Friends");
  if (groupName === null) return;
  await api("friends.update", { friend_id: friend.id, remark: remark.trim(), group_name: groupName.trim() || "Friends" });
  await refreshAll(false);
  showToast("好友信息已更新");
}

async function removeFriend(friend) {
  if (!friend) {
    showToast("请先选择一个好友");
    return;
  }
  if (!confirm(`确认删除好友 ${friendTitle(friend)}？`)) return;
  await api("friends.remove", { friend_id: friend.id });
  if (state.currentTarget?.kind === "direct" && Number(state.currentTarget.id) === Number(friend.id)) {
    state.currentTarget = null;
    els.appView.classList.remove("chat-open");
    renderMessages();
  }
  await refreshAll(false);
  showToast("好友已删除");
}

function openProfile() {
  const form = els.profileForm;
  form.uid.value = state.user.id || "";
  form.username.value = state.user.username || "";
  form.nickname.value = state.user.nickname || "";
  form.gender.value = state.user.gender || "保密";
  form.birthday.value = state.user.birthday || "";
  form.age.value = state.user.age || "";
  form.contact.value = state.user.contact || "";
  form.address.value = state.user.address || "";
  form.signature.value = state.user.signature || "";
  state.pendingAvatarFile = null;
  state.pendingAvatarCleared = false;
  paintAvatar(els.avatarPicker, state.user.avatar, state.user.nickname || state.user.username);
  els.profileDialog.showModal();
}

async function saveProfile(event) {
  event.preventDefault();
  let avatar = state.pendingAvatarCleared ? "" : state.user.avatar || "";
  if (state.pendingAvatarFile) {
    const upload = await uploadFile(state.pendingAvatarFile);
    avatar = `file:${upload.file.id}`;
  }
  const form = els.profileForm;
  const response = await api("profile.update", {
    nickname: form.nickname.value,
    gender: form.gender.value,
    birthday: form.birthday.value,
    age: form.age.value,
    contact: form.contact.value,
    address: form.address.value,
    signature: form.signature.value,
    avatar,
  });
  state.user = response.user;
  els.profileDialog.close();
  renderAll();
  showToast("资料已保存");
}

async function searchMessages() {
  const keyword = prompt("搜索消息关键词");
  if (!keyword) return;
  const response = await api("messages.search", { keyword: keyword.trim() });
  showMessageSearchResults(response.messages || [], keyword.trim());
}

function showMessageSearchResults(messages, keyword) {
  els.searchDialogMeta.textContent = messages.length ? `关键词“${keyword}”，找到 ${messages.length} 条消息` : `关键词“${keyword}”没有匹配消息`;
  els.searchResults.innerHTML = "";
  messages.slice(0, 100).forEach((message) => {
    const target = messageTarget(message);
    const context =
      target.kind === "group"
        ? groupTitle(findGroup(target.id) || { name: `群聊 ${target.id}` })
        : friendTitle(findFriend(target.id) || { username: `用户 ${target.id}` });
    const sender = message.sender_group_alias || message.sender_nickname || message.sender_username || "对方";
    const button = document.createElement("button");
    button.className = "result-item";
    button.innerHTML = `<div class="result-title"></div><div class="result-meta"></div><div class="result-preview"></div>`;
    button.querySelector(".result-title").textContent = context;
    button.querySelector(".result-meta").textContent = `${sender} · ${message.created_at || ""}`;
    button.querySelector(".result-preview").textContent = message.status === "recalled" ? "消息已撤回" : message.content || message.file_name || "";
    button.onclick = run(async () => {
      els.searchDialog.close();
      await openTarget(target);
    });
    els.searchResults.appendChild(button);
  });
  if (!messages.length) els.searchResults.innerHTML = `<div class="result-item"><div class="result-title">没有找到消息</div></div>`;
  if (!els.searchDialog.open) els.searchDialog.showModal();
}

function fileMessagesForCurrentTarget() {
  const rows = state.messages.get(targetKey(state.currentTarget)) || [];
  return rows.filter((message) => message.file_id && message.status !== "recalled");
}

function showFileDownloadDialog() {
  if (!state.currentTarget) {
    showToast("请先选择聊天对象");
    return;
  }
  const fileMessages = fileMessagesForCurrentTarget().slice().reverse();
  els.filesDialogMeta.textContent = fileMessages.length ? `当前会话共有 ${fileMessages.length} 个可保存文件` : "当前会话没有可保存文件";
  els.fileResults.innerHTML = "";
  fileMessages.forEach((message) => {
    const sender = Number(message.sender_id) === Number(state.user.id) ? "我" : message.sender_group_alias || message.sender_nickname || message.sender_username || "对方";
    const button = document.createElement("button");
    button.className = "result-item";
    button.innerHTML = `<div class="result-title"></div><div class="result-meta"></div><div class="result-preview"></div>`;
    button.querySelector(".result-title").textContent = message.file_name || `ochat_file_${message.file_id}`;
    button.querySelector(".result-meta").textContent = `${sender} · ${message.created_at || ""} · ${formatBytes(message.file_size)}`;
    button.querySelector(".result-preview").textContent = message.content || "";
    button.onclick = run(() => downloadFileMessage(message));
    els.fileResults.appendChild(button);
  });
  if (!fileMessages.length) els.fileResults.innerHTML = `<div class="result-item"><div class="result-title">没有可保存文件</div></div>`;
  if (!els.filesDialog.open) els.filesDialog.showModal();
}

async function downloadFileMessage(message) {
  const file = await loadFile(message.file_id);
  const binary = atob(file.content_b64);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
  const blob = new Blob([bytes], { type: file.mime_type || "application/octet-stream" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = file.filename || message.file_name || `ochat_file_${message.file_id}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function recallLastMessage() {
  if (!state.currentTarget) {
    showToast("请先选择聊天对象");
    return;
  }
  const rows = state.messages.get(targetKey(state.currentTarget)) || [];
  const mine = rows.filter((message) => Number(message.sender_id) === Number(state.user.id) && message.status !== "recalled");
  if (!mine.length) {
    showToast("当前聊天没有可撤回的自己消息");
    return;
  }
  await recallMessage(mine[mine.length - 1].id);
}

async function recallMessage(messageId) {
  await api("messages.recall", { message_id: Number(messageId) });
}

function buildEmojiPanel() {
  emojiList.forEach((emoji) => {
    const button = document.createElement("button");
    button.textContent = emoji;
    button.onclick = () => {
      els.messageInput.value += emoji;
      els.messageInput.focus();
    };
    els.emojiPanel.appendChild(button);
  });
}

async function openConfig() {
  const response = await api("bridge.config");
  els.configForm.host.value = response.host || "127.0.0.1";
  els.configForm.port.value = response.port || 8765;
  els.configDialog.showModal();
}

async function saveConfig(event) {
  event.preventDefault();
  const form = new FormData(els.configForm);
  const response = await api("bridge.config.update", {
    host: String(form.get("host") || "").trim(),
    port: Number(form.get("port") || 0),
  });
  els.configDialog.close();
  setAuthHint(`已连接到 ${response.host}:${response.port}`, "success");
}

async function bootstrap() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  const token = sessionStorage.getItem(TOKEN_STORAGE_KEY);
  if (!token) return;
  try {
    state.token = token;
    showApp(await api("resume", { token }));
  } catch {
    sessionStorage.removeItem(TOKEN_STORAGE_KEY);
  }
}

document.querySelectorAll("[data-auth-tab]").forEach((button) => {
  button.onclick = () => {
    document.querySelectorAll("[data-auth-tab]").forEach((item) => item.classList.toggle("active", item === button));
    els.loginForm.classList.toggle("hidden", button.dataset.authTab !== "login");
    els.registerForm.classList.toggle("hidden", button.dataset.authTab !== "register");
    setAuthHint();
  };
});

document.querySelectorAll("[data-password-toggle]").forEach((button) => {
  button.onclick = () => {
    const input = button.parentElement?.querySelector("input");
    if (!input) return;
    const visible = input.type === "text";
    input.type = visible ? "password" : "text";
    button.textContent = visible ? "显示" : "隐藏";
    button.setAttribute("aria-label", visible ? "显示密码" : "隐藏密码");
    input.focus();
  };
});

els.loginForm.onsubmit = async (event) => {
  event.preventDefault();
  if (els.loginSubmit.disabled) return;
  const form = new FormData(els.loginForm);
  setAuthLoading(els.loginSubmit, true);
  try {
    setAuthHint("正在为你连接 OCHAT...", "success");
    showApp(await api("login", Object.fromEntries(form.entries())));
  } catch (error) {
    setAuthHint(friendlyAuthError(error.message, "登录失败，请稍后重试。"), "error");
  } finally {
    setAuthLoading(els.loginSubmit, false);
  }
};

els.registerForm.onsubmit = async (event) => {
  event.preventDefault();
  if (els.registerSubmit.disabled) return;
  const form = new FormData(els.registerForm);
  setAuthLoading(els.registerSubmit, true);
  try {
    await api("register", Object.fromEntries(form.entries()));
    document.querySelector('[data-auth-tab="login"]').click();
    setAuthHint("账号创建好了，现在可以登录。", "success");
  } catch (error) {
    setAuthHint(friendlyAuthError(error.message, "注册失败，请检查信息后再试。"), "error");
  } finally {
    setAuthLoading(els.registerSubmit, false);
  }
};

document.querySelectorAll(".rail-button[data-mode]").forEach((button) => {
  button.onclick = () => {
    state.mode = button.dataset.mode;
    renderAll();
  };
});

document.querySelector("#addButton").onclick = run(() => {
  if (state.mode === "groups") return createGroup();
  if (state.mode === "requests") return refreshAll();
  return addFriend();
});
els.configButton.onclick = run(openConfig);
els.configForm.onsubmit = run(saveConfig);
els.sidebarToggleButton.onclick = toggleSidebar;
document.querySelector("#refreshButton").onclick = run(() => refreshAll());
document.querySelector("#logoutButton").onclick = run(async () => {
  state.pollVersion += 1;
  state.user = null;
  state.currentTarget = null;
  sessionStorage.removeItem(TOKEN_STORAGE_KEY);
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  await fetch("/api/logout", { method: "POST", headers: requestHeaders() });
  els.appView.classList.remove("chat-open");
  setSidebarCollapsed(false);
  els.appView.classList.add("hidden");
  els.authView.classList.remove("hidden");
});
document.querySelector("#profileButton").onclick = openProfile;
els.profileForm.onsubmit = run(saveProfile);
els.avatarPicker.onclick = () => els.avatarInput.click();
els.avatarInput.onchange = () => {
  const file = els.avatarInput.files?.[0];
  if (!file) return;
  state.pendingAvatarFile = file;
  state.pendingAvatarCleared = false;
  const url = URL.createObjectURL(file);
  els.avatarPicker.textContent = "";
  els.avatarPicker.style.backgroundImage = `url("${url}")`;
};
document.querySelector("#clearAvatarButton").onclick = () => {
  state.pendingAvatarFile = null;
  state.pendingAvatarCleared = true;
  paintAvatar(els.avatarPicker, "", state.user.nickname || state.user.username);
};
els.searchInput.oninput = debounce(renderList, 140);
els.sendButton.onclick = run(sendMessage);
els.messageInput.onkeydown = (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    run(sendMessage)();
  }
};
document.querySelector("#emojiButton").onclick = () => els.emojiPanel.classList.toggle("hidden");
document.querySelector("#fileButton").onclick = () => els.fileInput.click();
els.fileInput.onchange = run(() => sendPickedFile(els.fileInput.files?.[0]));
els.directProfileButton.onclick = showDirectProfile;
els.editFriendButton.onclick = run(() => editFriend(currentFriend()));
els.removeFriendButton.onclick = run(() => removeFriend(currentFriend()));
els.searchMessagesButton.onclick = run(searchMessages);
els.downloadFilesButton.onclick = showFileDownloadDialog;
els.recallButton.onclick = run(recallLastMessage);
els.groupPanelButton.onclick = run(openGroupPanel);
document.querySelector("#closeGroupDialog").onclick = () => els.groupDialog.close();
document.querySelector("#closeUserDialog").onclick = () => els.userDialog.close();
document.querySelector("#closeSearchDialog").onclick = () => els.searchDialog.close();
document.querySelector("#closeFilesDialog").onclick = () => els.filesDialog.close();

buildEmojiPanel();
bootstrap();
