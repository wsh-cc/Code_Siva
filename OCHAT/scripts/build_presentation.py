"""Build an OCHAT upgrade presentation without third-party packages."""

from __future__ import annotations

import html
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "ochat_upgrade_presentation.pptx"

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

SLIDES = [
    {
        "title": "OCHAT 在线互动聊天系统",
        "subtitle": "Python + Socket + Tkinter + MySQL 的聊天软件升级版",
        "bullets": ["面向课程答辩和本地演示", "新增未读消息与已读同步", "修复界面中文显示并增强可用性"],
    },
    {
        "title": "升级目标",
        "bullets": [
            "从“能发消息”升级到“像聊天软件一样可靠地沟通”",
            "服务端保存消息、文件、好友、群聊和已读状态",
            "客户端展示在线状态、历史记录、未读数、文件和撤回状态",
            "保持 Python 为主，方便理解、运行和答辩说明",
        ],
    },
    {
        "title": "核心功能",
        "bullets": [
            "账号注册、登录、退出和个人资料修改",
            "好友添加、删除、备注、分组与在线状态",
            "一对一私聊、群聊、群成员邀请和查看",
            "消息历史、关键词搜索、消息撤回",
            "文件/图片上传、发送、权限校验和保存",
            "未读消息统计与打开会话后自动清零",
        ],
    },
    {
        "title": "系统架构",
        "bullets": [
            "客户端：Tkinter 桌面界面，负责用户交互和事件刷新",
            "服务端：多线程 TCP Socket，处理协议分发、认证、广播",
            "协议层：JSON Lines + request_id，支持请求响应和实时事件",
            "存储层：MySQL 正式运行，SQLite 用于测试和快速演示",
            "安全层：密码哈希、参数校验、文件限制和权限检查",
        ],
    },
    {
        "title": "未读消息设计",
        "bullets": [
            "新增 message_reads 表，记录 user_id 与 message_id",
            "发送者自己的消息自动标为已读",
            "接收方未打开会话时，好友/群聊列表显示未读数",
            "打开历史或收到当前会话新消息时调用 messages.read",
            "服务端推送 unread.updated，保证多客户端同步",
        ],
    },
    {
        "title": "数据库模型",
        "bullets": [
            "users：账号、昵称、头像、签名、联系方式",
            "friendships：双向好友关系、备注和分组",
            "chat_groups / group_members：群聊信息、成员和角色",
            "messages：统一保存私聊与群聊消息",
            "files：保存文件元数据，真实文件存放在 uploads 目录",
            "message_reads：按用户记录已读状态",
        ],
    },
    {
        "title": "安全与可靠性",
        "bullets": [
            "PBKDF2-SHA256 + 随机盐保存密码摘要",
            "参数化 SQL 查询降低注入风险",
            "服务端统一校验好友关系、群成员身份和文件下载权限",
            "限制单包大小、文件大小、文件后缀和文件名",
            "断线、超时和非法请求返回明确错误",
        ],
    },
    {
        "title": "测试结果",
        "bullets": [
            "pytest 自动化测试覆盖协议、存储、安全、TCP 集成和客户端导入",
            "新增未读消息测试：私聊未读、群聊未读、读取后清零",
            "当前结果：20 passed",
            "SQLite 临时库让测试可重复运行，不污染真实 MySQL 数据",
        ],
    },
    {
        "title": "演示流程",
        "bullets": [
            "启动服务端：python start_server.py --db-backend sqlite --db database/ochat.db",
            "启动两个客户端：python start_client.py",
            "注册 Alice 和 Bob，互加好友后发送私聊消息",
            "观察 Bob 好友列表未读数，打开会话后未读清零",
            "创建群聊、邀请成员、发送群消息、演示搜索/撤回/文件发送",
        ],
    },
    {
        "title": "总结",
        "bullets": [
            "OCHAT 已具备聊天软件的基础闭环：账号、关系、会话、历史、文件和安全",
            "本次升级补齐了演示感最强的未读/已读体验",
            "后续可扩展方向：好友申请审核、消息编辑、语音视频、Web/移动端",
        ],
    },
]


SLIDES = [
    {
        "title": "OCHAT 在线互动聊天系统",
        "subtitle": "参考 QQ/微信 PC 端形态的 Python 聊天软件升级版",
        "bullets": ["三栏式 IM 界面", "完整个人资料页", "会话聚合接口", "申请/同意机制", "未读徽标与已读同步"],
    },
    {
        "title": "升级目标",
        "bullets": [
            "从“功能堆叠”升级到“会话优先”的真实聊天软件体验",
            "左侧功能栏、中间会话/联系人列表、右侧聊天窗口",
            "服务端统一聚合最后消息、未读数和在线状态",
            "保持 Python 为主，便于课程讲解、运行和二次扩展",
        ],
    },
    {
        "title": "新版界面",
        "bullets": [
            "左侧功能栏：消息、好友、群聊、资料、退出",
            "中间列表：搜索、会话预览、未读徽标、在线状态点",
            "申请页面：集中处理好友申请和群聊邀请",
            "右侧聊天：顶部资料区、气泡消息区、底部工具栏",
            "输入区支持多行输入，Enter 发送，Shift+Enter 换行",
            "工具栏集成表情、文件/图片、保存文件、消息撤回",
        ],
    },
    {
        "title": "个人资料界面",
        "bullets": [
            "点击左侧“资料”打开独立编辑窗口",
            "UID 和用户名只读展示，保证账号身份稳定",
            "支持修改昵称、生日、性别、年龄、住址",
            "支持修改联系方式、头像地址和个性签名",
            "客户端校验年龄格式，服务端校验字段长度和年龄范围",
        ],
    },
    {
        "title": "核心功能",
        "bullets": [
            "账号注册、登录、退出和完整个人资料修改",
            "好友添加、删除、备注、分组与在线状态",
            "好友申请、同意、拒绝和双向关系建立",
            "一对一私聊、群聊、群成员邀请和查看",
            "群邀请、同意入群、拒绝邀请",
            "消息历史、关键词搜索、消息撤回",
            "文件/图片上传、发送、权限校验和保存",
            "未读消息统计与打开会话后自动清零",
        ],
    },
    {
        "title": "系统架构",
        "bullets": [
            "客户端：Tkinter 桌面界面，负责交互和事件刷新",
            "服务端：多线程 TCP Socket，负责认证、协议分发和广播",
            "协议层：JSON Lines + request_id，支持请求响应和实时事件",
            "会话层：conversations.list 聚合私聊、群聊、最后消息和未读数",
            "申请层：friend_requests 与 group_invitations 持久化待处理状态",
            "存储层：MySQL 正式运行，SQLite 用于测试和快速演示",
        ],
    },
    {
        "title": "会话与未读设计",
        "bullets": [
            "新增 message_reads 表，记录 user_id 与 message_id",
            "发送者自己的消息自动标为已读",
            "接收方未打开会话时，会话列表显示未读数字徽标",
            "打开历史或收到当前会话新消息时调用 messages.read",
            "服务端推送 unread.updated，保证多客户端同步",
        ],
    },
    {
        "title": "申请/同意机制",
        "bullets": [
            "加好友不再直接成功，而是调用 friends.request 创建申请",
            "接收方在申请页同意后，服务端创建双向好友关系",
            "群邀请调用 groups.invite.request，只生成待处理邀请",
            "被邀请人同意后才写入 group_members，之后才能收发群消息",
            "requests.updated 事件让双方客户端实时刷新申请状态",
        ],
    },
    {
        "title": "数据库模型",
        "bullets": [
            "users：账号、昵称、头像、签名、联系方式",
            "users 扩展字段：生日、性别、住址、年龄",
            "friendships：双向好友关系、备注和分组",
            "friend_requests：好友申请、状态和处理时间",
            "chat_groups / group_members：群聊信息、成员和角色",
            "group_invitations：群邀请、接收人和处理状态",
            "messages：统一保存私聊与群聊消息",
            "files：保存文件元数据，真实文件存放在 uploads 目录",
            "message_reads：按用户记录已读状态",
        ],
    },
    {
        "title": "安全与可靠性",
        "bullets": [
            "PBKDF2-SHA256 + 随机盐保存密码摘要",
            "参数化 SQL 查询降低注入风险",
            "服务端统一校验好友关系、群成员身份和文件下载权限",
            "限制单包大小、文件大小、文件后缀和文件名",
            "断线、超时和非法请求返回明确错误",
        ],
    },
    {
        "title": "测试结果",
        "bullets": [
            "pytest 覆盖协议、存储、安全、TCP 集成和客户端导入",
            "新增会话聚合测试：标题、最后消息预览、未读数",
            "新增申请机制测试：好友申请同意/拒绝、群邀请同意/拒绝",
            "新增未读消息测试：私聊未读、群聊未读、读取后清零",
            "当前结果：28 passed",
        ],
    },
    {
        "title": "演示流程",
        "bullets": [
            "启动服务端：python start_server.py",
            "启动两个客户端：python start_client.py",
            "注册 Alice 和 Bob，互加好友后发送私聊消息",
            "演示好友申请：Alice 发起，Bob 在申请页同意",
            "演示群邀请：群主邀请，成员同意后入群",
            "观察 Bob 会话列表未读徽标，打开会话后未读清零",
            "创建群聊、邀请成员、发送群消息、演示搜索/撤回/文件发送",
        ],
    },
    {
        "title": "总结",
        "bullets": [
            "OCHAT 已从课程 Demo 升级为更接近真实 IM 的聊天软件",
            "会话聚合接口让客户端结构更清晰，后续扩展更自然",
            "后续可扩展好友申请审核、消息编辑、语音视频、Web/移动端",
        ],
    },
]


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def shape(shape_id: int, text: str, x: int, y: int, w: int, h: int, size: int, color: str = "172033", bold: bool = False) -> str:
    weight = ' b="1"' if bold else ""
    return f"""
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="{shape_id}" name="Text {shape_id}"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/><a:ln><a:noFill/></a:ln>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square"/>
          <a:lstStyle/>
          <a:p>
            <a:pPr><a:defRPr sz="{size * 100}"{weight}><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:defRPr></a:pPr>
            <a:r><a:rPr lang="zh-CN" sz="{size * 100}"{weight}/><a:t>{esc(text)}</a:t></a:r>
          </a:p>
        </p:txBody>
      </p:sp>"""


def bullet_shape(shape_id: int, bullets: list[str]) -> str:
    paragraphs = []
    for item in bullets:
        paragraphs.append(
            f"""
          <a:p>
            <a:pPr marL="360000" indent="-180000"><a:buChar char="•"/><a:defRPr sz="2200"><a:solidFill><a:srgbClr val="253047"/></a:solidFill></a:defRPr></a:pPr>
            <a:r><a:rPr lang="zh-CN" sz="2200"/><a:t>{esc(item)}</a:t></a:r>
          </a:p>"""
        )
    return f"""
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="{shape_id}" name="Bullets {shape_id}"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="950000" y="1850000"/><a:ext cx="10300000" cy="4200000"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/><a:ln><a:noFill/></a:ln>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square"/>
          <a:lstStyle/>
          {''.join(paragraphs)}
        </p:txBody>
      </p:sp>"""


def slide_xml(slide: dict[str, object], index: int) -> str:
    title = str(slide["title"])
    subtitle = str(slide.get("subtitle", ""))
    bullets = list(slide.get("bullets", []))
    subtitle_shape = shape(3, subtitle, 950000, 1220000, 10300000, 420000, 22, "536174") if subtitle else ""
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}">
  <p:cSld>
    <p:bg><p:bgPr><a:solidFill><a:srgbClr val="F5F7FB"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {shape(2, title, 950000, 620000, 10300000, 650000, 34, "111827", True)}
      {subtitle_shape}
      {bullet_shape(4, bullets)}
      {shape(5, f"OCHAT 升级版 · {index}/{len(SLIDES)}", 950000, 6420000, 10300000, 260000, 12, "6B7280")}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def content_types() -> str:
    slide_overrides = "\n".join(
        f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, len(SLIDES) + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
{slide_overrides}
</Types>"""


def presentation_xml() -> str:
    slide_ids = "\n".join(f'    <p:sldId id="{255 + i}" r:id="rId{i + 1}"/>' for i in range(1, len(SLIDES) + 1))
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>
{slide_ids}
  </p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""


def presentation_rels() -> str:
    rels = ['  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>']
    rels.extend(
        f'  <Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, len(SLIDES) + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
{chr(10).join(rels)}
</Relationships>"""


def static_parts() -> dict[str, str]:
    return {
        "_rels/.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>""",
        "docProps/core.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>OCHAT 升级版答辩演示</dc:title>
  <dc:creator>OCHAT</dc:creator>
  <cp:lastModifiedBy>OCHAT</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">2026-09-13T00:00:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">2026-09-13T00:00:00Z</dcterms:modified>
</cp:coreProperties>""",
        "docProps/app.xml": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>OCHAT Python Builder</Application>
  <Slides>{len(SLIDES)}</Slides>
</Properties>""",
        "ppt/slideMasters/slideMaster1.xml": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
</p:sldMaster>""",
        "ppt/slideMasters/_rels/slideMaster1.xml.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>""",
        "ppt/slideLayouts/slideLayout1.xml": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>""",
        "ppt/slideLayouts/_rels/slideLayout1.xml.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>""",
        "ppt/theme/theme1.xml": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="{A}" name="OCHAT">
  <a:themeElements>
    <a:clrScheme name="OCHAT"><a:dk1><a:srgbClr val="111827"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="253047"/></a:dk2><a:lt2><a:srgbClr val="F5F7FB"/></a:lt2><a:accent1><a:srgbClr val="2563EB"/></a:accent1><a:accent2><a:srgbClr val="10B981"/></a:accent2><a:accent3><a:srgbClr val="F59E0B"/></a:accent3><a:accent4><a:srgbClr val="EF4444"/></a:accent4><a:accent5><a:srgbClr val="6366F1"/></a:accent5><a:accent6><a:srgbClr val="14B8A6"/></a:accent6><a:hlink><a:srgbClr val="2563EB"/></a:hlink><a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink></a:clrScheme>
    <a:fontScheme name="OCHAT"><a:majorFont><a:latin typeface="Microsoft YaHei UI"/><a:ea typeface="Microsoft YaHei UI"/></a:majorFont><a:minorFont><a:latin typeface="Microsoft YaHei UI"/><a:ea typeface="Microsoft YaHei UI"/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="OCHAT"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="6350"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
  </a:themeElements>
</a:theme>""",
    }


def build() -> Path:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as deck:
        deck.writestr("[Content_Types].xml", content_types())
        deck.writestr("ppt/presentation.xml", presentation_xml())
        deck.writestr("ppt/_rels/presentation.xml.rels", presentation_rels())
        for name, content in static_parts().items():
            deck.writestr(name, content)
        for index, slide in enumerate(SLIDES, start=1):
            deck.writestr(f"ppt/slides/slide{index}.xml", slide_xml(slide, index))
            deck.writestr(
                f"ppt/slides/_rels/slide{index}.xml.rels",
                """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>""",
            )
    return OUT


if __name__ == "__main__":
    print(build())
