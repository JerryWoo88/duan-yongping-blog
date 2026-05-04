from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


PDF_PATH = Path(r"E:\电子书\段永平博客2006-2018文章合集（第1.0版）.pdf")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


HEADER_RE = re.compile(r"^2020/3/19\s+段永平博客.*$")
FILE_RE = re.compile(r"^ﬁle:///G\.HTM\s+\d+/\d+\s*$")
FOOTER_RE = re.compile(r"^本⽂档由\s+http://qicho\.ng/.*$")
ARTICLE_RE = re.compile(
    r"第\s*(\d+)\s*篇\s+(.+?)\n"
    r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})"
    r"\s+返回.{1,4}↑\s*\n"
    r"(http[^\n]+)\s*\n",
    re.S,
)
TOC_RE = re.compile(r"^\s*(\d+)\.\s+(\d{4}-\d{2}-\d{2})\s+(.+?)\s*$")


@dataclass
class Article:
    number: int
    date: str
    title: str
    url: str
    body: str
    comments: str

    @property
    def slug(self) -> str:
        return f"post-{self.number:03d}"


def clean_text(text: str) -> str:
    replacements = {
        "\ufb01": "fi",
        "\u2028": "\n",
        "\xa0": " ",
        "⾸": "首",
        "⽬": "目",
        "⽂": "文",
        "⽇": "日",
        "⽉": "月",
        "⼈": "人",
        "⼀": "一",
        "⼆": "二",
        "⼋": "八",
        "⼗": "十",
        "⼯": "工",
        "⼠": "士",
        "⼥": "女",
        "⼦": "子",
        "⼤": "大",
        "⼩": "小",
        "⼼": "心",
        "⼿": "手",
        "⼝": "口",
        "⼭": "山",
        "⼴": "广",
        "⻔": "门",
        "⻓": "长",
        "⻢": "马",
        "⻋": "车",
        "⻅": "见",
        "⻁": "虎",
        "⻛": "风",
        "⻩": "黄",
        "⾃": "自",
        "⾏": "行",
        "⾦": "金",
        "⾼": "高",
        "⾯": "面",
        "⾷": "食",
        "⿇": "麻",
        "⽆": "无",
        "⽤": "用",
        "⽣": "生",
        "⽼": "老",
        "⽐": "比",
        "⽽": "而",
        "⽶": "米",
        "⽹": "网",
        "⾃": "自",
        "⾥": "里",
        "⾜": "足",
        "⾝": "身",
        "⾔": "言",
        "⾛": "走",
        "⾞": "车",
        "⾰": "革",
        "⾮": "非",
        "⾄": "至",
        "⾄": "至",
        "⾼": "高",
        "⾮": "非",
        "⽅": "方",
        "⽀": "支",
        "⽐": "比",
        "⽓": "气",
        "⽔": "水",
        "⽕": "火",
        "⽇": "日",
        "⽆": "无",
        "⽂": "文",
        "⽩": "白",
        "⽬": "目",
        "⽯": "石",
        "⽴": "立",
        "⽿": "耳",
        "⾁": "肉",
        "⾊": "色",
        "⾏": "行",
        "⾐": "衣",
        "⾒": "见",
        "⾓": "角",
        "⾔": "言",
        "⾕": "谷",
        "⾦": "金",
        "⾟": "辛",
        "⾬": "雨",
        "⾴": "页",
        "⻚": "页",
        "⺠": "民",
        "⼊": "入",
        "⼏": "几",
        "⼒": "力",
        "⼜": "又",
        "⼟": "土",
        "⼼": "心",
        "⼤": "大",
        "⼩": "小",
        "⼲": "干",
        "⼴": "广",
        "⼸": "弓",
        "⼽": "戈",
        "⽉": "月",
        "⽊": "木",
        "⽎": "氏",
        "⽐": "比",
        "⽤": "用",
        "⽥": "田",
        "⽩": "白",
        "⽬": "目",
        "⽰": "示",
        "⽳": "穴",
        "⽵": "竹",
        "⽼": "老",
        "⽴": "立",
        "⽣": "生",
        "⾂": "臣",
        "⾄": "至",
        "⾛": "走",
        "⾜": "足",
        "⾝": "身",
        "⾞": "车",
        "⾥": "里",
        "⾨": "门",
        "⾮": "非",
        "⾯": "面",
        "⾹": "香",
        "⾹": "香",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def page_text(reader: PdfReader, page_index: int) -> str:
    text = reader.pages[page_index].extract_text() or ""
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            lines.append("")
            continue
        if HEADER_RE.match(line) or FILE_RE.match(line) or FOOTER_RE.match(line):
            continue
        lines.append(line)
    return clean_text("\n".join(lines))


def extract_articles(reader: PdfReader) -> list[Article]:
    cache = ROOT / "pdf-text-cache.txt"
    if cache.exists():
        full_text = cache.read_text(encoding="utf-8")
    else:
        full_text = "\n".join(page_text(reader, i) for i in range(26, len(reader.pages)))
        cache.write_text(full_text, encoding="utf-8")
    matches = list(ARTICLE_RE.finditer(full_text))
    articles: list[Article] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(full_text)
        raw = clean_text(full_text[start:end])
        body, sep, comments = raw.partition("文章评论")
        articles.append(
            Article(
                number=int(match.group(1)),
                title=clean_text(match.group(2).replace("\n", " ")),
                date=match.group(3),
                url=match.group(4).strip(),
                body=clean_text(body),
                comments=clean_text(comments) if sep else "",
            )
        )
    return articles


def extract_toc(reader: PdfReader) -> list[dict[str, str]]:
    toc_text = "\n".join(page_text(reader, i) for i in range(1, 27))
    rows = []
    current = ""
    for line in toc_text.splitlines():
        if TOC_RE.match(line):
            if current:
                rows.append(current)
            current = line
        elif current and not line.startswith("目 录"):
            current += " " + line.strip()
    if current:
        rows.append(current)

    toc = []
    for row in rows:
        match = TOC_RE.match(row)
        if match:
            toc.append({"number": int(match.group(1)), "date": match.group(2), "title": clean_text(match.group(3))})
    return toc


def paragraphs(text: str) -> str:
    if not text:
        return ""
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(parts) == 1:
        parts = [p.strip() for p in text.splitlines() if p.strip()]
    return "\n".join(f"<p>{html.escape(p)}</p>" for p in parts)


def comment_blocks(text: str) -> str:
    if not text:
        return '<p class="muted">无评论内容。</p>'
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    blocks = []
    current: list[str] = []
    marker = re.compile(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}")
    for line in lines:
        if marker.search(line) and current:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)

    html_blocks = []
    for block in blocks:
        head = html.escape(block[0])
        body = " ".join(html.escape(line) for line in block[1:])
        html_blocks.append(f'<div class="comment"><div class="comment-meta">{head}</div><p>{body}</p></div>')
    return "\n".join(html_blocks)


def render(articles: list[Article]) -> str:
    nav_items = "\n".join(
        f'<a href="#{a.slug}" data-title="{html.escape(a.title.lower())}">'
        f'<span>{a.number:03d}</span>{html.escape(a.date[:10])} {html.escape(a.title)}</a>'
        for a in articles
    )
    article_html = "\n".join(
        f"""
        <article class="post" id="{a.slug}">
          <header>
            <div class="post-kicker">第 {a.number} 篇 · {html.escape(a.date)}</div>
            <h2>{html.escape(a.title)}</h2>
            <a class="source" href="{html.escape(a.url)}" target="_blank" rel="noreferrer">原博客链接</a>
          </header>
          <section class="post-body">{paragraphs(a.body)}</section>
          <section class="comments">
            <h3>文章评论</h3>
            {comment_blocks(a.comments)}
          </section>
        </article>
        """
        for a in articles
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>段永平博客文章合集 2006-2018</title>
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <button class="nav-toggle" type="button" aria-controls="toc" aria-expanded="false">目录</button>
  <main class="layout">
    <section class="content">
      <header class="hero">
        <p>2006-2018 · 共 {len(articles)} 篇</p>
        <h1>段永平博客文章合集</h1>
        <div class="intro">由 PDF 文本整理成静态网页，目录固定在右侧，评论随各篇文章保留在正文之后。</div>
      </header>
      {article_html}
    </section>
    <aside class="toc" id="toc">
      <div class="toc-head">
        <strong>目录</strong>
        <input id="toc-search" type="search" placeholder="搜索标题或日期" autocomplete="off">
      </div>
      <nav>{nav_items}</nav>
    </aside>
  </main>
  <script src="assets/app.js"></script>
</body>
</html>
"""


def main() -> None:
    reader = PdfReader(str(PDF_PATH))
    articles = extract_articles(reader)
    toc = extract_toc(reader)
    if len(articles) != 584:
        raise SystemExit(f"Expected 584 articles, got {len(articles)}")
    DATA.mkdir(exist_ok=True)
    (DATA / "articles.json").write_text(
        json.dumps([a.__dict__ for a in articles], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (DATA / "toc.json").write_text(json.dumps(toc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(articles)} articles to {DATA}")


if __name__ == "__main__":
    main()
