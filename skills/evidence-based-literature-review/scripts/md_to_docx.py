#!/usr/bin/env python3
"""md_to_docx.py - convert the review's Markdown file into an editable Word (.docx) file.

Usage
  python md_to_docx.py review.md                 # writes review.docx next to it
  python md_to_docx.py review.md -o out.docx --font-latin "Times New Roman" --font-arabic "Simplified Arabic"

Standard library only (Python >= 3.9). No network access, no pip install.

Supported Markdown (what this skill writes): headings (#..####), paragraphs, **bold**,
*italic*, `code`, [links](url) and bare URLs/DOIs, bullet and numbered lists (3 levels),
pipe tables (with :--: alignment), > quotes, --- rules, fenced code blocks.
Direction is decided per paragraph from its first strong letter: Arabic -> RTL, Latin -> LTR,
so Arabic text and English reference entries are both laid out correctly in one document.
Paragraphs under a "References" / "المراجع" heading get a hanging indent.
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

RTL_CHARS = "\u0590-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFF"  # Hebrew/Arabic blocks and presentation forms
RTL_RE = re.compile(f"[{RTL_CHARS}]")
LTR_RE = re.compile(r"[A-Za-zÀ-ɏͰ-ϿЀ-ӿ]")
STRONG_RE = re.compile(f"[{RTL_CHARS}A-Za-zÀ-ɏͰ-ϿЀ-ӿ]")
REF_HEADING_RE = re.compile(r"^\s*(?:[\d٠-٩]+[.)\-]?\s*)?(references|reference list|bibliography|works cited|المراجع|قائمة المراجع|المصادر والمراجع)\b", re.I)

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
HR_RE = re.compile(r"^\s{0,3}([-*_])(\s*\1){2,}\s*$")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_RE = re.compile(
    r"(?P<code>`[^`]+`)"
    r"|(?P<bold>\*\*(?=\S)(?:.+?)(?<=\S)\*\*)"
    r"|(?P<ital>\*(?=[^\s*])(?:[^*]+?)(?<=[^\s*])\*)"
    r"|(?P<link>\[(?P<ltext>[^\]]+)\]\((?P<lurl>[^)\s]+)\))"
    r"|(?P<url>https?://[^\s<>()\[\]]+[^\s<>()\[\].,;:])"
)
ESCAPES = {"\\*": "\uE000", "\\_": "\uE001", "\\`": "\uE002", "\\|": "\uE003", "\\[": "\uE004", "\\]": "\uE005", "\\#": "\uE006"}
UNESCAPE = {v: k[1] for k, v in ESCAPES.items()}

PORTRAIT = '<w:pgSz w:w="11906" w:h="16838"/>'
LANDSCAPE = '<w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/>'
MARGINS = '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>'
WIDE_TABLE_COLS = 8  # tables with this many columns or more get landscape pages
TEXT_HEAVY_COLS = 6  # ...and so do tables from 6 columns whose rows are long prose
TEXT_HEAVY_ROW_CHARS = 200

W_NS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
)


def is_rtl(text: str) -> bool:
    m = STRONG_RE.search(text)
    return bool(m and RTL_RE.match(m.group(0)))


def protect(text: str) -> str:
    for k, v in ESCAPES.items():
        text = text.replace(k, v)
    return text


def restore(text: str) -> str:
    for k, v in UNESCAPE.items():
        text = text.replace(k, v)
    return text


# --------------------------------------------------------------------------
# inline formatting -> runs
# --------------------------------------------------------------------------
class Doc:
    def __init__(self, font_latin: str, font_arabic: str, size: int, size_cs: int):
        self.font_latin = font_latin
        self.font_arabic = font_arabic
        self.size = size
        self.size_cs = size_cs
        self.body: list[str] = []
        self.links: list[str] = []
        self.nums: list[str] = []  # "bullet" | "decimal" per w:num id (1-based)
        self.title = ""
        self.counts = {"paragraphs": 0, "tables": 0, "headings": 0}
        self.warnings: list[str] = []
        self.cur_rtl = False  # direction of the paragraph being built
        self.rtl_doc = False

    # -- runs --------------------------------------------------------------
    def run(self, text: str, b=False, i=False, code=False, link=False) -> str:
        """One logical run, split into script segments so Arabic gets w:rtl and Latin does not."""
        out = []
        for seg in split_scripts(restore(text), self.cur_rtl):
            rtl = bool(RTL_RE.search(seg))
            props = []
            if code:
                props.append('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>')
            if link:
                props.append('<w:color w:val="0563C1"/><w:u w:val="single"/>')
            if b:
                props.append("<w:b/><w:bCs/>")
            if i:
                props.append("<w:i/><w:iCs/>")
            if rtl:
                props.append("<w:rtl/>")
            rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
            out.append(f'<w:r>{rpr}<w:t xml:space="preserve">{escape(seg)}</w:t></w:r>')
        return "".join(out)

    def inline(self, text: str, b=False, i=False) -> str:
        text = protect(text)
        out, pos = [], 0
        for m in INLINE_RE.finditer(text):
            if m.start() > pos:
                out.append(self.run(text[pos:m.start()], b, i))
            if m.group("code"):
                out.append(self.run(m.group("code")[1:-1], b, i, code=True))
            elif m.group("bold"):
                out.append(self.inline(restore(m.group("bold")[2:-2]), True, i))
            elif m.group("ital"):
                out.append(self.inline(restore(m.group("ital")[1:-1]), b, True))
            elif m.group("link"):
                out.append(self.hyperlink(m.group("ltext"), m.group("lurl"), b, i))
            elif m.group("url"):
                out.append(self.hyperlink(m.group("url"), m.group("url"), b, i))
            pos = m.end()
        if pos < len(text):
            out.append(self.run(text[pos:], b, i))
        return "".join(out)

    def hyperlink(self, label: str, url: str, b: bool, i: bool) -> str:
        if url.startswith("#"):
            return self.run(label, b, i)
        self.links.append(restore(url))
        rid = f"rIdL{len(self.links)}"
        return f'<w:hyperlink r:id="{rid}" w:history="1">{self.run(label, b, i, link=True)}</w:hyperlink>'

    # -- blocks ------------------------------------------------------------
    def para(self, content_xml: str, rtl: bool, style: str | None = None, extra_ppr: str = "", jc: str | None = None):
        ppr = []
        if style:
            ppr.append(f'<w:pStyle w:val="{style}"/>')
        ppr.append(extra_ppr)
        if rtl:
            ppr.append("<w:bidi/>")
        if jc:
            ppr.append(f'<w:jc w:val="{jc}"/>')
        self.counts["paragraphs"] += 1
        return f"<w:p><w:pPr>{''.join(ppr)}</w:pPr>{content_xml}</w:p>"

    def new_num(self, kind: str) -> int:
        self.nums.append(kind)
        return len(self.nums)


OPENERS = "([{\"'“‘«"


def split_scripts(text: str, para_rtl: bool = False) -> list[str]:
    """Split into runs of one script so each run gets the right direction.

    Neutral characters follow the preceding run, except at a script boundary:
    opening brackets/quotes move to the run they open, and boundary spaces go to the
    run written in the paragraph's own direction (as Word does when typing).
    """
    segs: list[list] = []  # [text, rtl]
    cur, cur_rtl = "", None
    for ch in text:
        if STRONG_RE.match(ch):
            r = bool(RTL_RE.match(ch))
            if cur_rtl is None:
                cur_rtl = r
            elif r != cur_rtl:
                segs.append([cur, cur_rtl])
                cur, cur_rtl = "", r
        cur += ch
    if cur:
        segs.append([cur, cur_rtl])
    for k in range(len(segs) - 1):
        a, b = segs[k], segs[k + 1]
        stripped = a[0].rstrip(OPENERS)
        moved = a[0][len(stripped):]
        if moved and stripped.strip():
            a[0], b[0] = stripped, moved + b[0]
        if a[1] != para_rtl:
            body = a[0].rstrip()
            if body:
                b[0] = a[0][len(body):] + b[0]
                a[0] = body
    if not para_rtl:
        # In a left-to-right paragraph only the Arabic letters themselves run right-to-left:
        # "(العتيبي, 2022)" must read name-then-year, so brackets, commas and digits stay LTR.
        trimmed: list[list] = []
        for t, r in segs:
            hits = [k for k, ch in enumerate(t) if RTL_RE.match(ch)] if r else []
            if not hits:
                trimmed.append([t, False if r else r])
                continue
            a, b = hits[0], hits[-1] + 1
            trimmed += [[t[:a], False], [t[a:b], True], [t[b:], False]]
        segs = []
        for t, r in trimmed:
            if not t:
                continue
            if segs and segs[-1][1] == r:
                segs[-1][0] += t
            else:
                segs.append([t, r])
    out = []
    for t, r in segs:
        # An embedded citation such as "(Smith & Lee, 2020)" must not wrap: a line break inside
        # a run of the opposite direction scatters its brackets across two lines.
        if r is not None and r != para_rtl and re.fullmatch(r"\s*[(\[][^()\[\]]{1,60}[)\]][.,;:]?\s*", t):
            core = t.strip()
            t = t[: len(t) - len(t.lstrip())] + core.replace(" ", "\u00A0") + t[len(t.rstrip()):]
        if t:
            out.append(t)
    return out


# --------------------------------------------------------------------------
# block parser
# --------------------------------------------------------------------------
def split_row(line: str) -> list[str]:
    line = protect(line.strip())
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [restore(c.strip()) for c in line.split("|")]


def convert(md: str, doc: Doc) -> None:
    lines = md.replace("\r\n", "\n").split("\n")
    # drop YAML frontmatter if present
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() == "---":
                lines = lines[j + 1:]
                break
    i, n = 0, len(lines)
    in_refs = False
    last_heading = None
    list_state: dict[int, int] = {}  # level -> num id for the current list block

    def flush_list():
        list_state.clear()

    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            flush_list()
            continue

        if FENCE_RE.match(line):
            fence = FENCE_RE.match(line).group(1)
            i += 1
            while i < n and not lines[i].strip().startswith(fence):
                doc.body.append(doc.para(doc.run(lines[i] or " ", code=True), False, "CodeBlock"))
                i += 1
            i += 1
            flush_list()
            continue

        m = HEADING_RE.match(line)
        if m:
            level = min(len(m.group(1)), 4)
            text = m.group(2)
            if not doc.title:
                doc.title = re.sub(r"[*`]", "", text)
            in_refs = bool(REF_HEADING_RE.match(re.sub(r"[*`#]", "", text)))
            doc.cur_rtl = is_rtl(text)
            last_heading = doc.para(doc.inline(text), doc.cur_rtl, f"Heading{level}")
            doc.body.append(last_heading)
            doc.counts["headings"] += 1
            i += 1
            flush_list()
            continue

        if HR_RE.match(line):
            doc.body.append(doc.para("", False, "Rule"))
            i += 1
            flush_list()
            continue

        if line.lstrip().startswith("|") and i + 1 < n and TABLE_SEP_RE.match(lines[i + 1]):
            header = split_row(line)
            aligns = []
            for c in split_row(lines[i + 1]):
                c = c.strip()
                aligns.append("center" if c.startswith(":") and c.endswith(":") else "right" if c.endswith(":") else None)
            rows = []
            i += 2
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            ncols = max([len(header)] + [len(r) for r in rows])
            avg_row = sum(len("".join(r)) for r in rows) / max(len(rows), 1)
            wide = ncols >= WIDE_TABLE_COLS or (ncols >= TEXT_HEAVY_COLS and avg_row >= TEXT_HEAVY_ROW_CHARS)
            if wide:  # close the portrait section, put the table (and its heading) in a landscape section
                at = len(doc.body) - 1 if doc.body and doc.body[-1] is last_heading else len(doc.body)
                end_section(doc, at, PORTRAIT)
            doc.body.append(table_xml(doc, header, rows, aligns, wide))
            if wide:
                end_section(doc, len(doc.body), LANDSCAPE)
            doc.counts["tables"] += 1
            flush_list()
            continue

        if line.lstrip().startswith(">"):
            quote = []
            while i < n and lines[i].lstrip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            for chunk in "\n".join(quote).split("\n\n"):
                text = " ".join(x.strip() for x in chunk.split("\n") if x.strip())
                if text:
                    doc.cur_rtl = is_rtl(text)
                    side = (
                        '<w:pBdr><w:left w:val="nil"/><w:right w:val="single" w:sz="12" w:space="8" w:color="A5A5A5"/></w:pBdr>'
                        if doc.cur_rtl else ""
                    )
                    doc.body.append(doc.para(doc.inline(text), doc.cur_rtl, "Quote", side))
            flush_list()
            continue

        m = LIST_RE.match(line)
        if m:
            indent = len(m.group(1).replace("\t", "    "))
            level = min(indent // 2, 2)
            kind = "decimal" if m.group(2)[0].isdigit() else "bullet"
            text = m.group(3)
            i += 1
            while i < n and lines[i].strip() and not LIST_RE.match(lines[i]) and lines[i].startswith((" ", "\t")) \
                    and not HEADING_RE.match(lines[i].strip()):
                text += " " + lines[i].strip()
                i += 1
            text = re.sub(r"^\[ \]\s*", "☐ ", re.sub(r"^\[[xX]\]\s*", "☑ ", text))
            if in_refs:  # APA: reference entries are hanging-indent paragraphs, never bullets
                doc.cur_rtl = is_rtl(text)
                doc.body.append(doc.para(doc.inline(text), doc.cur_rtl, None, '<w:ind w:left="720" w:hanging="720"/>'))
                continue
            for deeper in [lv for lv in list_state if lv > level]:
                del list_state[deeper]
            key = level
            if key not in list_state or doc.nums[list_state[key] - 1] != kind:
                list_state[key] = doc.new_num(kind)
            num = list_state[key]
            ppr = f'<w:numPr><w:ilvl w:val="{level}"/><w:numId w:val="{num}"/></w:numPr>'
            if text[:1] in "☐☑":  # task item: the box replaces the bullet
                ppr = f'<w:ind w:left="{360 * (level + 1)}"/>'
            doc.cur_rtl = is_rtl(text)
            doc.body.append(doc.para(doc.inline(text), doc.cur_rtl, "ListParagraph", ppr))
            continue

        # paragraph: join following plain lines
        para_lines = [line.strip()]
        i += 1
        while i < n and lines[i].strip() and not (
            HEADING_RE.match(lines[i]) or LIST_RE.match(lines[i]) or FENCE_RE.match(lines[i])
            or HR_RE.match(lines[i]) or lines[i].lstrip().startswith((">", "|"))
        ):
            para_lines.append(lines[i].strip())
            i += 1
        text = " ".join(x.rstrip("\\").strip() for x in para_lines)
        if re.search(r"!\[[^\]]*\]\(", text):
            doc.warnings.append("images are not embedded; their alt text is kept")
            text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
        extra = '<w:ind w:left="720" w:hanging="720"/>' if in_refs else ""
        doc.cur_rtl = is_rtl(text)
        doc.body.append(doc.para(doc.inline(text), doc.cur_rtl, None, extra, "both" if not in_refs else None))
        flush_list()


def end_section(doc: Doc, at: int, size: str) -> None:
    """End the section just before body index `at` with the given page size.

    The sectPr goes into the preceding paragraph, as Word does, so no extra line is
    added. After a table there is no paragraph to reuse, so a 1pt-high one carries it;
    a normal-height empty paragraph would spill onto a blank page when the table
    fills the last page.
    """
    sect = f"<w:sectPr>{size}{MARGINS}" + ("<w:bidi/>" if doc.rtl_doc else "") + "</w:sectPr>"
    prev = doc.body[at - 1] if at > 0 else ""
    if prev.startswith("<w:p><w:pPr>") and "<w:sectPr>" not in prev:
        doc.body[at - 1] = prev.replace("</w:pPr>", sect + "</w:pPr>", 1)
        return
    tiny = '<w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/><w:rPr><w:sz w:val="2"/><w:szCs w:val="2"/></w:rPr>'
    doc.body.insert(at, f"<w:p><w:pPr>{tiny}{sect}</w:pPr></w:p>")


def table_xml(doc: Doc, header: list[str], rows: list[list[str]], aligns: list, wide: bool = False) -> str:
    ncols = max([len(header)] + [len(r) for r in rows])
    rtl = is_rtl(" ".join(header))

    def cell(text: str, col: int, head: bool) -> str:
        jc = aligns[col] if col < len(aligns) else None
        shade = '<w:shd w:val="clear" w:color="auto" w:fill="E7E6E6"/>' if head else ""
        doc.cur_rtl = is_rtl(text) if text.strip() else rtl
        content = doc.inline(text, b=head) if text else ""
        p = doc.para(content, doc.cur_rtl, "TableText", "", jc)
        return f'<w:tc><w:tcPr><w:tcW w:w="0" w:type="auto"/>{shade}</w:tcPr>{p}</w:tc>'

    def row(cells: list[str], head: bool) -> str:
        cells = cells + [""] * (ncols - len(cells))
        trpr = "<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>" if head else "<w:trPr><w:cantSplit/></w:trPr>"
        return f"<w:tr>{trpr}{''.join(cell(c, k, head) for k, c in enumerate(cells))}</w:tr>"

    grid = "".join('<w:gridCol w:w="%d"/>' % ((13900 if wide else 9000) // ncols) for _ in range(ncols))
    bidi = "<w:bidiVisual/>" if rtl else ""
    return (
        f'<w:tbl><w:tblPr><w:tblStyle w:val="ReviewTable"/>{bidi}<w:tblW w:w="5000" w:type="pct"/>'
        f'<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>'
        f"</w:tblPr><w:tblGrid>{grid}</w:tblGrid>{row(header, True)}{''.join(row(r, False) for r in rows)}</w:tbl>"
        + ("" if wide else "<w:p/>")
    )


# --------------------------------------------------------------------------
# package parts
# --------------------------------------------------------------------------
def styles_xml(doc: Doc) -> str:
    fl, fa = escape(doc.font_latin), escape(doc.font_arabic)
    sz, szc = doc.size * 2, doc.size_cs * 2

    def heading(level: int, pt: int) -> str:
        return (
            f'<w:style w:type="paragraph" w:styleId="Heading{level}"><w:name w:val="heading {level}"/>'
            f'<w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="9"/><w:qFormat/>'
            f'<w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="{360 if level == 1 else 240}" w:after="120" w:line="276" w:lineRule="auto"/>'
            f'<w:outlineLvl w:val="{level - 1}"/></w:pPr>'
            f'<w:rPr><w:b/><w:bCs/><w:color w:val="1F3864"/><w:sz w:val="{pt * 2}"/><w:szCs w:val="{(pt + 2) * 2}"/></w:rPr></w:style>'
        )

    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles {W_NS}>
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="{fl}" w:hAnsi="{fl}" w:eastAsia="{fl}" w:cs="{fa}"/>
<w:sz w:val="{sz}"/><w:szCs w:val="{szc}"/><w:lang w:val="en-US" w:eastAsia="en-US" w:bidi="ar-SA"/></w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="360" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>
{heading(1, 16)}{heading(2, 14)}{heading(3, 13)}{heading(4, 12)}
<w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:spacing w:after="60"/><w:contextualSpacing/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:ind w:left="720" w:right="720"/><w:pBdr><w:left w:val="single" w:sz="12" w:space="8" w:color="A5A5A5"/></w:pBdr></w:pPr>
<w:rPr><w:i/><w:iCs/><w:color w:val="404040"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="CodeBlock"><w:name w:val="Code Block"/><w:basedOn w:val="Normal"/>
<w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/><w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="TableText"><w:name w:val="Table Text"/><w:basedOn w:val="Normal"/>
<w:pPr><w:spacing w:before="40" w:after="40" w:line="240" w:lineRule="auto"/></w:pPr>
<w:rPr><w:sz w:val="{max(sz - 4, 16)}"/><w:szCs w:val="{max(szc - 4, 16)}"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Rule"><w:name w:val="Horizontal Rule"/><w:basedOn w:val="Normal"/>
<w:pPr><w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="A5A5A5"/></w:pBdr></w:pPr></w:style>
<w:style w:type="table" w:styleId="ReviewTable"><w:name w:val="Review Table"/><w:tblPr>
<w:tblBorders><w:top w:val="single" w:sz="4" w:color="808080"/><w:left w:val="single" w:sz="4" w:color="808080"/>
<w:bottom w:val="single" w:sz="4" w:color="808080"/><w:right w:val="single" w:sz="4" w:color="808080"/>
<w:insideH w:val="single" w:sz="4" w:color="808080"/><w:insideV w:val="single" w:sz="4" w:color="808080"/></w:tblBorders>
<w:tblCellMar><w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>
</w:styles>"""


def numbering_xml(doc: Doc) -> str:
    def levels(kind: str) -> str:
        out = []
        bullets = ["•", "◦", "▪"]
        for lv in range(3):
            fmt = "decimal" if kind == "decimal" else "bullet"
            text = f"%{lv + 1}." if kind == "decimal" else bullets[lv]
            ind = 720 * (lv + 1)
            out.append(
                f'<w:lvl w:ilvl="{lv}"><w:start w:val="1"/><w:numFmt w:val="{fmt}"/><w:lvlText w:val="{text}"/>'
                f'<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="{ind}" w:hanging="360"/></w:pPr></w:lvl>'
            )
        return "".join(out)

    abstract = (
        f'<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="hybridMultilevel"/>{levels("bullet")}</w:abstractNum>'
        f'<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="hybridMultilevel"/>{levels("decimal")}</w:abstractNum>'
    )
    nums = "".join(
        f'<w:num w:numId="{k}"><w:abstractNumId w:val="{0 if kind == "bullet" else 1}"/>'
        + ("".join(f'<w:lvlOverride w:ilvl="{lv}"><w:startOverride w:val="1"/></w:lvlOverride>' for lv in range(3))
           if kind == "decimal" else "")
        + "</w:num>"
        for k, kind in enumerate(doc.nums, 1)
    )
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:numbering {W_NS}>{abstract}{nums}</w:numbering>'


def build_docx(doc: Doc, out: Path, rtl_doc: bool) -> None:
    sect = f"<w:sectPr>{PORTRAIT}{MARGINS}" + ("<w:bidi/>" if rtl_doc else "") + "</w:sectPr>"
    document = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:document {W_NS}><w:body>'
        + "".join(doc.body) + sect + "</w:body></w:document>"
    )
    links = "".join(
        f'<Relationship Id="rIdL{k}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" '
        f'Target="{escape(url, {chr(34): "&quot;"})}" TargetMode="External"/>'
        for k, url in enumerate(doc.links, 1)
    )
    rels_doc = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
        + links + "</Relationships>"
    )
    settings = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:settings {W_NS}>'
        '<w:defaultTabStop w:val="720"/><w:characterSpacingControl w:val="doNotCompress"/>'
        '<w:themeFontLang w:val="en-US" w:bidi="ar-SA"/></w:settings>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
        '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '</Types>'
    )
    rels_root = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '</Relationships>'
    )
    core = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/">'
        f"<dc:title>{escape(doc.title)}</dc:title></cp:coreProperties>"
    )
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels_root)
        z.writestr("docProps/core.xml", core)
        z.writestr("word/document.xml", document)
        z.writestr("word/styles.xml", styles_xml(doc))
        z.writestr("word/numbering.xml", numbering_xml(doc))
        z.writestr("word/settings.xml", settings)
        z.writestr("word/_rels/document.xml.rels", rels_doc)


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    p = argparse.ArgumentParser(description="Convert a Markdown literature review into an editable .docx file.")
    p.add_argument("markdown", help="input .md file")
    p.add_argument("-o", "--output", help="output .docx (default: same name next to the input)")
    p.add_argument("--font-latin", default="Times New Roman")
    p.add_argument("--font-arabic", default="Simplified Arabic")
    p.add_argument("--size", type=int, default=12, help="Latin font size in pt (default 12)")
    p.add_argument("--size-arabic", type=int, default=14, help="Arabic font size in pt (default 14)")
    args = p.parse_args(argv)

    src = Path(args.markdown)
    if not src.is_file():
        print(f"error: {src} not found", file=sys.stderr)
        return 2
    out = Path(args.output) if args.output else src.with_suffix(".docx")
    md = src.read_text(encoding="utf-8-sig")
    doc = Doc(args.font_latin, args.font_arabic, args.size, args.size_arabic)
    doc.rtl_doc = len(RTL_RE.findall(md)) > len(LTR_RE.findall(md))
    convert(md, doc)
    build_docx(doc, out, rtl_doc=doc.rtl_doc)
    c = doc.counts
    print(f"wrote {out}  ({c['headings']} headings, {c['paragraphs']} paragraphs, {c['tables']} tables, {len(doc.links)} links)")
    for w in sorted(set(doc.warnings)):
        print(f"warning: {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
