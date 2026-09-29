#!/usr/bin/env python3
"""Sinh data.js cho Bản đồ kiến thức iOS từ PROGRESS.vi.md và các file chủ đề .vi.md.

Dùng:
  python3 Docs/KnowledgeMap/build.py
      Đọc source, sinh lại Docs/KnowledgeMap/data.js.

  python3 Docs/KnowledgeMap/build.py --done Swift/Protocols --undone Swift/ARC
      Tick / bỏ tick chủ đề trong PROGRESS.md và PROGRESS.vi.md, rồi sinh lại data.js.
      Bảng có nút "Sao chép lệnh" tạo sẵn lệnh này.

Mỗi file chủ đề được tách theo các mục `##`:
  - "Câu hỏi luyện tập" / "Câu hỏi thực hành"  -> danh sách câu hỏi
  - "Đáp án câu hỏi luyện tập"                  -> mỗi `###` là một câu hỏi kèm câu trả lời
  - "Bẫy phỏng vấn"                             -> mỗi `###` là một bẫy, gồm
                                                   **Dễ trả lời sai:** và **Nên trả lời:**
  - "Bài tập"                                   -> tab Bài tập
  - các mục còn lại                             -> tab Bài học, hiển thị đầy đủ
"""
import argparse
import html
import json
import posixpath
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "data.js"
PROGRESS_SOURCE = ROOT / "PROGRESS.vi.md"
PROGRESS_FILES = [ROOT / "PROGRESS.vi.md", ROOT / "PROGRESS.md"]
REPO_URL = "https://github.com/codewizardVN/review-ios/blob/main/"

# Liên kết chéo giữa các chủ đề (đường nét đứt trên bảng). Key = đường dẫn không có đuôi.
LINKS = [
    ("Swift/ARC", "Performance/MemoryLeaks"),
    ("Concurrency/Actors", "Performance/MainThread"),
    ("Swift/Protocols", "Testing/Mocking"),
    ("Architecture/DependencyInjection", "Testing/TestableDesign"),
    ("SwiftUI/DependencyInjection", "Architecture/DependencyInjection"),
    ("Networking/Codable", "Networking/RequestResponseMapping"),
    ("SwiftUI/UIKitInterop", "UIKit/ViewControllerLifecycle"),
    ("UIKit/Coordinator", "SwiftUI/Navigation"),
    ("Architecture/Coordinator", "UIKit/Coordinator"),
    ("UIKit/DeepLinks", "UIKit/PushNotifications"),
    ("Networking/OfflineFirst", "Persistence/CoreData"),
    ("Networking/OfflineFirst", "Persistence/SwiftData"),
    ("Concurrency/AsyncAwait", "Networking/URLSession"),
    ("Performance/LargeListOptimization", "UIKit/CollectionViewDiffable"),
    ("Performance/StartupTime", "Architecture/Modularization"),
    ("Senior/CrashReportingAnalytics", "Senior/ProductionDebugging"),
    ("Senior/FeatureFlagsExperimentation", "Senior/ReleaseProcess"),
    ("Testing/UITests", "Accessibility/Accessibility"),
    ("Concurrency/Combine", "SwiftUI/StateManagement"),
    ("Architecture/MVVM", "SwiftUI/StateManagement"),
    ("Security/Keychain", "Security/NetworkSecurity"),
    ("SwiftUI/WidgetsLiveActivities", "UIKit/PushNotifications"),
    ("Architecture/CleanArchitecture", "Networking/RequestResponseMapping"),
    ("UIKit/BackgroundExecution", "Networking/URLSession"),
    ("Senior/CICD", "Testing/SnapshotTests"),
]

DAY_RE = re.compile(r"^##\s+(?:Ngày|Day)\s+(\d+)\s+[—–-]\s+(.+?)\s*$")
ITEM_RE = re.compile(r"^(- \[)( |x|X)(\] \[(.+?)\]\(\./(.+?)\))")
BULLET_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")

QUESTION_SECTIONS = ("câu hỏi luyện tập", "câu hỏi thực hành")
ANSWER_SECTION = "đáp án câu hỏi"
TRAP_SECTION = "bẫy phỏng vấn"
EXERCISE_SECTION = "bài tập"
SUMMARY_SECTIONS = ("ý chính", "ý tưởng chính")
WRONG_LABEL = "Dễ trả lời sai:"
RIGHT_LABEL = "Nên trả lời:"


def topic_key(path: str) -> str:
    path = path.strip().lstrip("./")
    return re.sub(r"(\.vi)?\.md$", "", path)


# ---------------------------------------------------------------- markdown -> HTML

def inline(text: str, base: str) -> str:
    """Inline markdown: `code`, **bold**, *italic*, [link](url)."""
    codes = []

    def keep(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep, text)
    text = html.escape(text, quote=False)

    def link(m):
        label, url = m.group(1), m.group(2)
        if url.startswith(("http://", "https://")):
            href = url
        elif url.endswith(".md") or ".md#" in url:
            href = REPO_URL + posixpath.normpath(posixpath.join(posixpath.dirname(base), url))
        else:
            return label
        return f'<a href="{html.escape(href)}" target="_blank" rel="noopener">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def md_to_html(lines, base: str) -> str:
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()
        if not s or s == "---":
            i += 1
            continue
        if s.startswith("```"):
            lang = s[3:].strip()
            body = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            cls = f' class="lang-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(body))}</code></pre>")
            continue
        m = re.match(r"^(#{3,6})\s+(.*)$", s)
        if m:
            level = min(len(m.group(1)) + 1, 6)
            text = re.sub(r"^\d+\.\s*", "", m.group(2))
            out.append(f"<h{level}>{inline(text, base)}</h{level}>")
            i += 1
            continue
        if s.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                head = "".join(f"<th>{inline(c, base)}</th>" for c in rows[0])
                body = "".join("<tr>" + "".join(f"<td>{inline(c, base)}</td>" for c in r) + "</tr>" for r in rows[1:])
                out.append(f'<div class="tbl"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
            continue
        if s.startswith(">"):
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(f"<blockquote>{inline(' '.join(quote), base)}</blockquote>")
            continue
        if BULLET_RE.match(line):
            html_list, i = parse_list(lines, i, base)
            out.append(html_list)
            continue
        para = []
        while i < n and lines[i].strip() and not re.match(r"^\s*(```|#|\||>|---\s*$)", lines[i]) and not BULLET_RE.match(lines[i]):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para), base)}</p>")
    return "".join(out)


def parse_list(lines, i, base):
    """Danh sách lồng nhau theo độ thụt lề."""
    first = BULLET_RE.match(lines[i])
    indent, ordered = len(first.group(1)), first.group(2)[0].isdigit()
    items = []
    while i < len(lines):
        line = lines[i]
        m = BULLET_RE.match(line)
        if not line.strip():
            # Dòng trống: danh sách tiếp tục nếu dòng kế tiếp vẫn là item cùng cấp.
            j = i + 1
            if j < len(lines) and (mm := BULLET_RE.match(lines[j])) and len(mm.group(1)) >= indent:
                i = j
                continue
            break
        if m and len(m.group(1)) == indent:
            items.append([inline(m.group(3), base)])
            i += 1
        elif m and len(m.group(1)) > indent and items:
            sub, i = parse_list(lines, i, base)
            items[-1].append(sub)
        elif not m and items and line.startswith(" " * (indent + 2)):
            items[-1][0] += " " + inline(line.strip(), base)
            i += 1
        else:
            break
    tag = "ol" if ordered else "ul"
    return f"<{tag}>" + "".join(f"<li>{''.join(parts)}</li>" for parts in items) + f"</{tag}>", i


def plain(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(text))).strip()


# ---------------------------------------------------------------- topic parsing

def split_sections(lines):
    """Trả về (title, intro_lines, [(heading, lines)]) theo các mục `##`; bỏ qua code block khi dò heading."""
    title, intro, sections, current, in_code = None, [], [], None, False
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
        if not in_code and re.match(r"^#\s+", line) and title is None:
            title = line[2:].strip()
            continue
        if not in_code and re.match(r"^##\s+", line):
            current = (line[3:].strip(), [])
            sections.append(current)
            continue
        if current is None:
            if title is not None and not line.startswith("["):
                intro.append(line)
        else:
            current[1].append(line)
    return title, intro, sections


def split_h3(lines):
    """Tách các khối `### ...` (bỏ qua code block)."""
    blocks, cur, in_code = [], None, False
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
        if not in_code and re.match(r"^###\s+", line):
            cur = (line[4:].strip(), [])
            blocks.append(cur)
        elif cur is not None:
            cur[1].append(line)
    return blocks


def bullets_of(lines):
    return [re.sub(r"\*\*|`", "", m.group(3)).strip() for l in lines if (m := BULLET_RE.match(l)) and not m.group(1)]


def parse_traps(lines, base):
    traps = []
    for title, body in split_h3(lines):
        parts, key = {"wrong": [], "right": [], "note": []}, "note"
        for line in body:
            s = line.strip()
            for label, k in ((WRONG_LABEL, "wrong"), (RIGHT_LABEL, "right")):
                if s.startswith(f"**{label}**"):
                    key, line = k, s[len(label) + 4:].strip()
            parts[key].append(line)
        traps.append({
            "title": plain(inline(title, base)),
            "wrong": md_to_html(parts["wrong"], base),
            "right": md_to_html(parts["right"] or parts["note"], base),
        })
    return traps


def parse_topic(path: Path, rel: str) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    title, intro, sections = split_sections(lines)
    lesson, questions, answers, traps, exercise, summary = [], [], [], [], "", ""

    if any(l.strip() for l in intro):
        lesson.append({"h": "", "html": md_to_html(intro, rel)})
    for heading, body in sections:
        low = heading.lower()
        if ANSWER_SECTION in low:  # kiểm tra trước: tiêu đề này cũng chứa "câu hỏi luyện tập"
            answers = [{"q": plain(inline(q, rel)), "html": md_to_html(b, rel)} for q, b in split_h3(body)]
        elif any(k in low for k in QUESTION_SECTIONS):
            questions += [q for q in bullets_of(body) if q not in questions]
        elif TRAP_SECTION in low:
            traps = parse_traps(body, rel)
        elif low.startswith(EXERCISE_SECTION):
            exercise = md_to_html(body, rel)
        else:
            block = md_to_html(body, rel)
            lesson.append({"h": plain(inline(re.sub(r"^\d+\.\s*", "", heading), rel)), "html": block})
            if not summary and any(k in low for k in SUMMARY_SECTIONS):
                m = re.search(r"<p>(.*?)</p>", block)
                summary = plain(m.group(1)) if m else ""

    if not summary:
        for sec in lesson:
            m = re.search(r"<p>(.*?)</p>", sec["html"])
            if m:
                summary = plain(m.group(1))
                break

    # Có mục đáp án thì dùng nó; chưa có thì vẫn hiện câu hỏi để biết còn thiếu.
    qa = answers or [{"q": q, "html": ""} for q in questions]

    return {
        "title": plain(inline(title or path.stem, rel)),
        "summary": summary,
        "lesson": lesson,
        "qa": qa,
        "traps": traps,
        "exercise": exercise,
        "text": " ".join(plain(s["html"]) for s in lesson) + " " + " ".join(t["title"] for t in traps),
    }


def parse_progress():
    days, current = [], None
    for line in PROGRESS_SOURCE.read_text(encoding="utf-8").splitlines():
        m = DAY_RE.match(line)
        if m:
            current = {"day": int(m.group(1)), "name": m.group(2).strip(), "topics": []}
            days.append(current)
            continue
        if line.startswith("## "):
            current = None
            continue
        m = ITEM_RE.match(line)
        if m and current is not None:
            current["topics"].append({
                "key": topic_key(m.group(5)),
                "label": m.group(4).strip(),
                "done": m.group(2).lower() == "x",
            })
    return days


def build():
    days = parse_progress()
    missing, unanswered, no_traps = [], [], []
    for day in days:
        for t in day["topics"]:
            t["file"] = f"{t['key']}.vi.md"
            path = ROOT / t["file"]
            if not path.exists():
                missing.append(t["file"])
                continue
            t.update(parse_topic(path, t["file"]))
            if any(not qa["html"] for qa in t["qa"]):
                unanswered.append(t["key"])
            if not t["traps"]:
                no_traps.append(t["key"])
    known = {t["key"] for d in days for t in d["topics"]}
    links = [list(pair) for pair in LINKS if pair[0] in known and pair[1] in known]

    data = {"source": PROGRESS_SOURCE.name, "repo": REPO_URL, "days": days, "links": links}
    OUT.write_text(
        "// Tự sinh bởi build.py từ PROGRESS.vi.md và các file .vi.md. Đừng sửa tay.\n"
        "window.KNOWLEDGE_MAP = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    topics = [t for d in days for t in d["topics"]]
    print(f"Đã sinh {OUT.relative_to(ROOT)}: {len(days)} ngày, {len(topics)} chủ đề, "
          f"{sum(t['done'] for t in topics)} đã tick, {len(links)} liên kết, "
          f"{sum(len(t.get('qa', [])) for t in topics)} câu hỏi, {sum(len(t.get('traps', [])) for t in topics)} bẫy.")
    for f in missing:
        print(f"  Cảnh báo: không tìm thấy {f}", file=sys.stderr)
    for label, keys in (("Chưa có đáp án câu hỏi", unanswered), ("Chưa có mục Bẫy phỏng vấn", no_traps)):
        if keys:
            shown = " ".join(keys[:6]) + (" …" if len(keys) > 6 else "")
            print(f"  {label}: {len(keys)} chủ đề ({shown})", file=sys.stderr)


def set_progress(done_keys, undone_keys):
    wanted = {topic_key(k): True for k in done_keys}
    wanted.update({topic_key(k): False for k in undone_keys})
    seen = set()
    for f in PROGRESS_FILES:
        lines = f.read_text(encoding="utf-8").splitlines(keepends=True)
        for i, line in enumerate(lines):
            m = ITEM_RE.match(line)
            if not m:
                continue
            key = topic_key(m.group(5))
            if key in wanted:
                seen.add(key)
                lines[i] = m.group(1) + ("x" if wanted[key] else " ") + line[m.end(2):]
        f.write_text("".join(lines), encoding="utf-8")
    for key in wanted:
        state = "tick" if wanted[key] else "bỏ tick"
        print(f"{'✓' if key in seen else '✗ không tìm thấy'} {state}: {key}")
    if not seen:
        sys.exit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--done", nargs="*", default=[], metavar="TOPIC", help="tick chủ đề, ví dụ Swift/Protocols")
    ap.add_argument("--undone", nargs="*", default=[], metavar="TOPIC", help="bỏ tick chủ đề")
    args = ap.parse_args()
    if args.done or args.undone:
        set_progress(args.done, args.undone)
    build()
