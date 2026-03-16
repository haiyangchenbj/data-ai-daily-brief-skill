# -*- coding: utf-8 -*-
"""
Data+AI Daily Brief — 企业微信推送脚本
自动识别日报文件，提取3层优先级摘要并推送到企业微信群。

摘要提取策略（v2.0）:
  层级1（必选）: 大标题 + 今日变化（精简版）+ 总判断（精简版）
  层级2（必选）: 各板块标题 + 每条新闻标题行
  层级3（可选）: 每条新闻一句完整摘要，按剩余字节空间填充

用法:
  python send_wecom.py                        # 推送今天的日报
  python send_wecom.py 2026-03-10             # 推送指定日期的日报
  python send_wecom.py --webhook <url>        # 使用自定义 webhook
  python send_wecom.py --force                # 强制重推（忽略防重复锁）
  python send_wecom.py --md-only              # 仅推送摘要，不推送 HTML

环境变量:
  WECOM_WEBHOOK_URL  — 企业微信 Webhook 地址（优先级高于配置文件）
"""
import json
import urllib.request
import os
import sys
import re
import argparse
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
CONFIG_FILE = PROJECT_DIR / "daily-brief-config.json"


def load_config():
    """加载配置文件。"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_webhook_url(args_webhook=None):
    """获取 Webhook URL，优先级：命令行参数 > 环境变量 > 配置文件。"""
    if args_webhook:
        return args_webhook

    env_url = os.environ.get("WECOM_WEBHOOK_URL")
    if env_url:
        return env_url

    config = load_config()
    wechat_config = config.get("adapters", {}).get("wechatwork", {})
    url = wechat_config.get("webhook_url", "")
    if url:
        return url

    print("[错误] 未配置企微 Webhook URL")
    print("  方式 1: 设置环境变量 WECOM_WEBHOOK_URL")
    print("  方式 2: 在 daily-brief-config.json 中配置")
    print("  方式 3: 使用 --webhook 参数")
    sys.exit(1)


def find_file(date_str, ext, search_dirs=None):
    """查找指定日期的日报文件。支持多种命名模式和搜索路径。"""
    if search_dirs is None:
        search_dirs = [PROJECT_DIR, Path(".")]

    patterns = [
        f"Data+AI全球日报_{date_str}.{ext}",
        f"Data+AI全球日报_{date_str}_v3.{ext}",
        f"Data+AI全球日报_{date_str}_v2.{ext}",
    ]

    for directory in search_dirs:
        for name in patterns:
            path = directory / name
            if path.exists():
                return path
    return None


# ─────────────────────────────────────────────────────────
# 摘要提取核心算法（v2.0 三层优先级填充）
# ─────────────────────────────────────────────────────────

def _extract_first_complete_sentence(text):
    """从文本中提取第一个语义完整的句子。

    规则：
    1. 按句号/分号切分，取第一句
    2. 如果结果以冒号结尾（引导句，如"核心论点包括："），
       说明不是自足句，返回 None
    3. 如果整段没有句号/分号，取前80字符并加省略号
    """
    if not text:
        return None

    first_sent = text
    for sep in ["。", "；"]:
        si = first_sent.find(sep)
        if si != -1:
            first_sent = first_sent[:si + 1]
            break

    # 检查是否以冒号结尾（引导句 — 后面跟列表，截取后会"半句"）
    if first_sent.rstrip().endswith("：") or first_sent.rstrip().endswith(":"):
        return None

    # 如果截取后仍然很长，限制长度
    if len(first_sent) > 100:
        for ci in range(80, min(len(first_sent), 100)):
            if first_sent[ci] in "，,、":
                first_sent = first_sent[:ci + 1].rstrip("，,、") + "。"
                break
        else:
            first_sent = first_sent[:80] + "..."

    return first_sent


def _truncate_line_to_bytes(text, max_bytes):
    """将文本截断到指定字节数内，在字符边界处截断。"""
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    for i in range(len(text), 0, -1):
        if len(text[:i].encode("utf-8")) <= max_bytes - 6:
            return text[:i] + "..."
    return "..."


def extract_summary_from_md(md_path):
    """从 Markdown 文件中提取精简摘要（不超过 4096 字节）。

    三层优先级填充策略:
      层级1（必选）: 大标题 + "今日最重要的N个变化"（精简版）+ 总判断（精简版）
      层级2（必选）: 各板块标题（## A. ~ ## E.）+ 每条新闻的标题行
      层级3（可选，按空间填充）: 每条新闻的一句完整摘要

    关键特性:
      - 今日变化每条限制在一句话内（去掉长篇说明）
      - 总判断截取核心观点，不保留细节展开
      - 层级3首句必须是语义完整的句子，不纳入"...包括："类引导句
      - 摘要中不带任何链接，来源链接仅在 HTML 完整版中呈现
      - 严格 4096 字节控制（按 UTF-8 字节计算）
    """
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")

    # ── 层级1: 大标题 + 今日变化（精简）+ 总判断（精简）──
    layer1_lines = []
    in_top_changes = False
    found_summary_judgment = False

    for line in lines:
        stripped = line.strip()

        # 大标题 (# Data+AI ...)
        if stripped.startswith("# ") and not stripped.startswith("## "):
            layer1_lines.append(stripped)
            continue

        # "今日最重要的N个变化" 标题
        if stripped.startswith("## 今日") or stripped.startswith("## 🔥"):
            in_top_changes = True
            layer1_lines.append("")
            layer1_lines.append(stripped)
            continue

        if in_top_changes:
            if stripped.startswith("## ") or stripped == "---":
                in_top_changes = False
            else:
                # 总判断可能在今日变化区域内
                if not found_summary_judgment and (
                    stripped.startswith("**总判断") or
                    stripped.startswith("> **总判断") or
                    stripped.startswith("> 总判断")
                ):
                    judgment = stripped
                    if len(judgment.encode("utf-8")) > 250:
                        judgment = _truncate_line_to_bytes(judgment, 250)
                    layer1_lines.append("")
                    layer1_lines.append(judgment)
                    found_summary_judgment = True
                # 编号条目：截取一句话
                elif re.match(r"^\d+\.\s+\*\*", stripped):
                    sent = stripped
                    for sep in ["。", "；"]:
                        si = sent.find(sep)
                        if si != -1 and si < len(sent) - 1:
                            sent = sent[:si + 1]
                            break
                    if len(sent.encode("utf-8")) > 200:
                        sent = _truncate_line_to_bytes(sent, 200)
                    layer1_lines.append(sent)
                continue

        # 总判断（在今日变化区域外）
        if not found_summary_judgment and (
            stripped.startswith("**总判断") or
            stripped.startswith("> **总判断") or
            stripped.startswith("> 总判断")
        ):
            judgment = stripped
            if len(judgment.encode("utf-8")) > 250:
                judgment = _truncate_line_to_bytes(judgment, 250)
            layer1_lines.append("")
            layer1_lines.append(judgment)
            found_summary_judgment = True
            continue

    # ── 层级2: 板块标题 + 每条新闻标题 ──
    layer2_lines = []       # [(行文本, 唯一标记 or None)]
    layer3_candidates = []  # [(唯一标记, 摘要首句文本)]

    current_section = None
    current_item_idx = None
    in_layer2_zone = False
    pending_summary_lines = []
    pending_summary_item = None

    def _flush_multiline_summary():
        """处理多行摘要：如果首行是引导句，从后续列表项提取首条内容。"""
        nonlocal pending_summary_lines, pending_summary_item
        if not pending_summary_lines or not pending_summary_item:
            pending_summary_lines = []
            pending_summary_item = None
            return

        first_line = pending_summary_lines[0]
        sent = _extract_first_complete_sentence(first_line)

        if sent is None:
            for sub_line in pending_summary_lines[1:]:
                clean = sub_line.strip()
                clean = re.sub(r"^[-*]\s*", "", clean)
                clean = re.sub(r"^\*\*[^*]+\*\*[：:]\s*", "", clean)
                sent = _extract_first_complete_sentence(clean)
                if sent:
                    break

        if sent:
            layer3_candidates.append((
                pending_summary_item,
                f'> <font color="comment">{sent}</font>'
            ))

        pending_summary_lines = []
        pending_summary_item = None

    collecting_summary = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # 板块标题: ## A. ~ ## E.
        section_match = re.match(r"^## ([A-E])\.", stripped)
        if section_match:
            if collecting_summary:
                _flush_multiline_summary()
                collecting_summary = False
            layer2_lines.append(("", None))
            layer2_lines.append(("---", None))
            layer2_lines.append((stripped, None))
            current_section = section_match.group(1)
            current_item_idx = None
            in_layer2_zone = True
            continue

        if not in_layer2_zone:
            continue

        # 新闻标题: ### 数字. 标题
        m = re.match(r"^###\s+(\d+)\.\s+(.+)", stripped)
        if m:
            if collecting_summary:
                _flush_multiline_summary()
                collecting_summary = False
            item_num = m.group(1)
            item_title = m.group(2)
            current_item_idx = f"{current_section}-{item_num}"
            layer2_lines.append((f"{item_num}. {item_title}", current_item_idx))
            continue

        # 跳过 **来源** 行
        if stripped.startswith("**来源**") or stripped.startswith("- **来源**"):
            if collecting_summary:
                _flush_multiline_summary()
                collecting_summary = False
            continue

        # **摘要** 开始行
        if stripped.startswith("**摘要**") or stripped.startswith("**摘要：**"):
            if collecting_summary:
                _flush_multiline_summary()
            colon_idx = stripped.find("：")
            if colon_idx == -1:
                colon_idx = stripped.find(":")
            if colon_idx != -1:
                after_colon = stripped[colon_idx + 1:].strip()
                if after_colon:
                    pending_summary_lines = [after_colon]
                    pending_summary_item = current_item_idx
                    collecting_summary = True
            continue

        # 多行摘要收集
        if collecting_summary:
            if stripped == "" or stripped.startswith("**") or stripped.startswith("## "):
                _flush_multiline_summary()
                collecting_summary = False
                if stripped.startswith("**") and not stripped.startswith("## "):
                    continue
            else:
                if len(pending_summary_lines) < 3:
                    pending_summary_lines.append(stripped)
                continue

        # blockquote 留空板块说明
        if stripped.startswith("> 本期") and current_item_idx is None:
            layer2_lines.append((stripped, None))
            continue

        # Watchlist 的 **情况** 行
        if stripped.startswith("**情况**") or stripped.startswith("**情况：**"):
            colon_idx = stripped.find("：")
            if colon_idx == -1:
                colon_idx = stripped.find(":")
            if colon_idx != -1:
                after_colon = stripped[colon_idx + 1:].strip()
                sent = _extract_first_complete_sentence(after_colon)
                if current_item_idx and sent:
                    layer3_candidates.append((
                        current_item_idx,
                        f'> <font color="comment">{sent}</font>'
                    ))
            continue

        # Analyst Insights 的 **核心论点与数据**
        if stripped.startswith("**核心论点") or stripped.startswith("**机构**"):
            continue

    # 结束时处理未 flush 的摘要
    if collecting_summary:
        _flush_multiline_summary()

    # ── 组装最终摘要 ──
    tail = "\n\n> 完整版见下方 HTML 文档"
    MAX_BYTES = 4096

    # 组装层级1 + 层级2
    base_parts = ["\n".join(layer1_lines).strip()]
    base_parts.append("")
    for text, _ in layer2_lines:
        base_parts.append(text)
    base_text = "\n".join(base_parts).strip()

    # 剥离 Markdown 链接
    base_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', base_text)

    # 加尾部
    base_with_tail = base_text + tail
    base_bytes = len(base_with_tail.encode("utf-8"))

    if base_bytes > MAX_BYTES:
        target = MAX_BYTES - len(tail.encode("utf-8"))
        for ci in range(len(base_text), 0, -1):
            if len(base_text[:ci].encode("utf-8")) <= target:
                return base_text[:ci] + tail
        return tail

    # 有剩余空间，尝试插入层级3
    remaining = MAX_BYTES - base_bytes
    final_lines = base_with_tail.split("\n")

    marker_to_text = {}
    for text, marker in layer2_lines:
        if marker:
            marker_to_text[marker] = text

    insertions = []
    for marker, summary_text in layer3_candidates:
        summary_bytes = len(("\n" + summary_text).encode("utf-8"))
        if summary_bytes > remaining:
            continue
        title_text = marker_to_text.get(marker)
        if not title_text:
            continue
        for li, fline in enumerate(final_lines):
            if fline.strip() == title_text.strip():
                insertions.append((li + 1, summary_text))
                remaining -= summary_bytes
                break

    insertions.sort(key=lambda x: x[0], reverse=True)
    for li, text in insertions:
        final_lines.insert(li, text)

    return "\n".join(final_lines)


# ─────────────────────────────────────────────────────────
# 推送与防重复
# ─────────────────────────────────────────────────────────

def check_send_lock(date_str):
    """检查是否已经推送过该日期的日报。"""
    lock_dir = PROJECT_DIR / ".send_locks"
    lock_file = lock_dir / f"{date_str}.lock"
    return lock_file.exists()


def create_send_lock(date_str):
    """创建推送锁文件，记录推送时间。"""
    lock_dir = PROJECT_DIR / ".send_locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_file = lock_dir / f"{date_str}.lock"
    with open(lock_file, "w", encoding="utf-8") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def send_markdown(webhook_url, content):
    """推送 Markdown 消息到企微。"""
    payload = {"msgtype": "markdown", "markdown": {"content": content}}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    print(f"  摘要长度: {len(content)} 字符 / {len(content.encode('utf-8'))} 字节")
    req = urllib.request.Request(
        webhook_url, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print(f"  [摘要] errcode: {result.get('errcode')}, errmsg: {result.get('errmsg')}")
        return result


def upload_and_send_file(webhook_url, filepath):
    """上传文件并推送到企微。"""
    upload_url = webhook_url.replace("/send?", "/upload_media?") + "&type=file"
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        file_data = f.read()

    boundary = "----PythonBoundary7MA4YWxk"
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"media\"; filename=\"{filename}\"\r\n"
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        upload_url, data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        media_id = result.get("media_id")
        print(f"  [上传] errcode: {result.get('errcode')}, media_id: {media_id}")

    if media_id:
        payload = {"msgtype": "file", "file": {"media_id": media_id}}
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            webhook_url, data=data,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            print(f"  [文档] errcode: {result.get('errcode')}, errmsg: {result.get('errmsg')}")


def main():
    parser = argparse.ArgumentParser(description="Data+AI 日报企微推送")
    parser.add_argument("date", nargs="?", default=None, help="日期 YYYY-MM-DD（默认今天）")
    parser.add_argument("--webhook", help="企微 Webhook URL")
    parser.add_argument("--md-only", action="store_true", help="仅推送摘要，不推送 HTML 文件")
    parser.add_argument("--force", action="store_true", help="强制重推（忽略防重复锁）")
    parser.add_argument("--search-dir", action="append", help="额外搜索日报文件的目录")
    args = parser.parse_args()

    # 确定日期
    if args.date:
        try:
            dt = datetime.strptime(args.date, "%Y-%m-%d")
            date_str = dt.strftime("%Y-%m-%d")
        except ValueError:
            print(f"[错误] 日期格式无效: {args.date}，应为 YYYY-MM-DD")
            sys.exit(1)
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")

    webhook_url = get_webhook_url(args.webhook)

    # 搜索目录
    search_dirs = [PROJECT_DIR, Path(".")]
    if args.search_dir:
        search_dirs.extend(Path(d) for d in args.search_dir)

    print("=" * 55)
    print(f"  Data+AI Daily Brief — 企微推送")
    print(f"  目标日期: {date_str}")
    print("=" * 55)

    # 防重复推送检查
    if check_send_lock(date_str) and not args.force:
        print(f"\n[跳过] {date_str} 的日报已推送过。")
        print(f"  如需重新推送，请使用: python send_wecom.py {date_str} --force")
        sys.exit(0)

    # 查找 MD 文件
    md_path = find_file(date_str, "md", search_dirs)
    if not md_path:
        print(f"\n[错误] 未找到 {date_str} 的 Markdown 日报文件")
        sys.exit(1)
    print(f"\n[MD] {md_path.name}")

    # 查找 HTML 文件
    html_path = find_file(date_str, "html", search_dirs) if not args.md_only else None
    if html_path:
        print(f"[HTML] {html_path.name}")

    # 推送精简摘要
    print(f"\n步骤 1/2: 从 MD 提取摘要并推送...")
    summary = extract_summary_from_md(md_path)
    send_markdown(webhook_url, summary)

    # 推送 HTML 完整版
    if html_path:
        print(f"\n步骤 2/2: 推送完整版 HTML 文档...")
        upload_and_send_file(webhook_url, str(html_path))
    else:
        print(f"\n步骤 2/2: 跳过（无 HTML 文件或 --md-only）")

    # 记录推送锁
    create_send_lock(date_str)
    if args.force:
        print(f"\n  (已使用 --force 强制重推)")

    print("\n" + "=" * 55)
    print("  推送完成!")
    print("=" * 55)


if __name__ == "__main__":
    main()
