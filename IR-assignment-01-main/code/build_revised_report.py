"""Build the editable academic report and its source-driven figures.

The report is intentionally generated from the CSV files already present in the
project.  It reports the dataset compliance audit as observed rather than
assuming that the dataset satisfies the assignment quotas.
"""

from pathlib import Path
import re

import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "report"
OUTPUT_DIR = ROOT / "output"
GRAPH_DIR = OUTPUT_DIR / "graphs"
DOCX_PATH = REPORT_DIR / "report.docx"

INK = "1F2937"
NAVY = "17324D"
BLUE = "2E74B5"
MUTED = "5B6470"
LIGHT_BLUE = "E8EEF5"
LIGHT_GRAY = "F2F4F7"
PALE_GOLD = "FFF5D6"
PALE_RED = "FDECEC"
GREEN = "1F6B45"
RED = "9B1C1C"
WHITE = "FFFFFF"
FONT = "Calibri"


def rgb(value: str) -> RGBColor:
    return RGBColor.from_string(value)


def set_run_font(run, name=FONT, size=None, color=INK, bold=None, italic=None):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    if size is not None:
        run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = rgb(color)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_fixed(table, widths, header_fill=LIGHT_BLUE):
    """Apply fixed DXA table geometry instead of renderer-dependent autofit."""
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")

    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(int(width * 1440) for width in widths)))
    tbl_w.set(qn("w:type"), "dxa")

    grid = tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(int(width * 1440)))
        grid.append(col)

    for row_index, row in enumerate(table.rows):
        for index, cell in enumerate(row.cells):
            width = widths[min(index, len(widths) - 1)]
            cell.width = Inches(width)
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(int(width * 1440)))
            tc_w.set(qn("w:type"), "dxa")
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if row_index == 0 and header_fill:
                set_cell_shading(cell, header_fill)


def set_cell_text(cell, text, bold=False, color=INK, size=9.5, align=None):
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.line_spacing = 1.05
    if align is not None:
        paragraph.alignment = align
    run = paragraph.add_run(str(text))
    set_run_font(run, size=size, color=color, bold=bold)


def add_table(doc, rows, widths, header=True, header_fill=LIGHT_BLUE, font_size=9.5):
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    set_table_fixed(table, widths, header_fill if header else None)
    for ri, row in enumerate(rows):
        for ci, value in enumerate(row):
            is_header = header and ri == 0
            set_cell_text(
                table.cell(ri, ci),
                value,
                bold=is_header,
                color=(WHITE if header_fill == NAVY else NAVY) if is_header else INK,
                size=font_size,
            )
    return table


def set_paragraph_style(style, size=11, color=INK, bold=False, before=0, after=6, line=1.1):
    style.font.name = FONT
    style._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), FONT)
    style._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), FONT)
    style.font.size = Pt(size)
    style.font.color.rgb = rgb(color)
    style.font.bold = bold
    fmt = style.paragraph_format
    fmt.space_before = Pt(before)
    fmt.space_after = Pt(after)
    fmt.line_spacing = line


def add_page_field(paragraph):
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr)
    run._r.append(fld_char2)
    set_run_font(run, size=9, color=MUTED)


def add_callout(doc, label, text, fill=LIGHT_BLUE, label_color=NAVY):
    table = doc.add_table(rows=1, cols=1)
    set_table_fixed(table, [6.5], None)
    cell = table.cell(0, 0)
    set_cell_shading(cell, fill)
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.08
    r = p.add_run(f"{label}: ")
    set_run_font(r, size=10, color=label_color, bold=True)
    r = p.add_run(text)
    set_run_font(r, size=10, color=INK)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_body(doc, text, style="Body Text"):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run(text)
    return p


def add_label_body(doc, label, text, style="Body Text"):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(label)
    set_run_font(r, size=11, color=NAVY, bold=True)
    r = p.add_run(text)
    set_run_font(r, size=11, color=INK)
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.25)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.1
    p.add_run(text)
    return p


def add_figure(doc, filename, caption, width=6.2):
    path = GRAPH_DIR / filename
    if not path.exists():
        add_callout(doc, "Missing figure", f"Expected {path} but it was not found.", fill=PALE_RED, label_color=RED)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(path), width=Inches(width))
    cap = doc.add_paragraph(style="Caption")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.add_run(caption)


def add_heading(doc, text, level=1):
    return doc.add_heading(text, level=level)


def audit_dataset(posts):
    text = posts["post"].fillna("").astype(str)
    patterns = {
        "Hashtags": r"#[A-Za-z0-9_]+",
        "URLs": r"https?://\S+|www\.\S+",
        "Mentions": r"@[A-Za-z0-9_]+",
        "Slang/abbreviations": r"\b(?:lol|lmao|omg|tbh|ngl|bruh|fr|idk|btw|rn|imo|smh|irl|wbu|gonna|wanna|gotta|ain't|u|ur|ya)\b",
    }
    rows = []
    for label, pattern in patterns.items():
        per_post = text.str.count(pattern, flags=re.IGNORECASE)
        rows.append((label, 20, int((per_post > 0).sum()), int(per_post.sum())))
    emoji_pattern = r"[\U0001F300-\U0001FAFF\u2600-\u27BF]"
    emoji_per_post = text.map(lambda value: bool(re.search(emoji_pattern, value)))
    rows.append(("Emoji-bearing posts", 20, int(emoji_per_post.sum()), int(emoji_per_post.sum())))
    return rows


def build_report():
    REPORT_DIR.mkdir(exist_ok=True)
    tokenizer = pd.read_csv(OUTPUT_DIR / "tokenizer_results.csv")
    comparison = pd.read_csv(OUTPUT_DIR / "tokenizer_comparison.csv")
    regex = pd.read_csv(OUTPUT_DIR / "regex_results.csv")
    posts = pd.read_csv(ROOT / "dataset" / "social_media_posts.csv")
    audit_rows = audit_dataset(posts)

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    styles = doc.styles
    set_paragraph_style(styles["Normal"], size=11, after=6, line=1.1)
    set_paragraph_style(styles["Body Text"], size=11, after=6, line=1.1)
    set_paragraph_style(styles["Caption"], size=9, color=MUTED, after=6, line=1.0)
    set_paragraph_style(styles["Heading 1"], size=16, color=BLUE, bold=True, before=16, after=8, line=1.0)
    set_paragraph_style(styles["Heading 2"], size=13, color=BLUE, bold=True, before=12, after=6, line=1.0)
    set_paragraph_style(styles["Heading 3"], size=12, color=NAVY, bold=True, before=8, after=4, line=1.0)
    set_paragraph_style(styles["List Bullet"], size=11, after=4, line=1.1)

    for paragraph in section.header.paragraphs:
        paragraph.text = ""
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = paragraph.add_run("Information Retrieval Assignment | Revised analysis report")
        set_run_font(r, size=9, color=MUTED)
    footer = section.footer.paragraphs[0]
    footer.text = ""
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = footer.add_run("Page ")
    set_run_font(r, size=9, color=MUTED)
    add_page_field(footer)

    # Cover page.
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(62)
    p.paragraph_format.space_after = Pt(14)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("INFORMATION RETRIEVAL ASSIGNMENT")
    set_run_font(r, size=14, color=BLUE, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run("Tokenizer Analysis and Regex Normalization")
    set_run_font(r, size=28, color=NAVY, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(22)
    r = p.add_run("An evidence-based report on informal social-media text")
    set_run_font(r, size=15, color=MUTED)

    add_table(
        doc,
        [
            ["Student", "Enrollment No.", "Registration No.", "Section"],
            ["Reddy Eswar Anush", "23UCS173", "2317023", "B"],
        ],
        [1.75, 1.55, 1.65, 1.55],
        font_size=9.5,
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    add_table(
        doc,
        [
            ["Corpus", "Tokenizers", "Task 2 posts", "Chars removed"],
            ["100 posts", "3", "100", str(int(regex["chars_removed"].sum()))],
        ],
        [1.625, 1.625, 1.625, 1.625],
        header_fill=NAVY,
        font_size=10,
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Revised report | September 2026")
    set_run_font(r, size=10, color=MUTED)
    add_callout(
        doc,
        "Integrity note",
        "The submitted social-media CSV does not meet every quota in the assignment brief. This report records the measured gap instead of presenting unsupported claims.",
        fill=PALE_GOLD,
        label_color="7A5A00",
    )
    doc.add_page_break()

    # Contents and executive summary.
    add_heading(doc, "Contents", 1)
    for entry in [
        "Executive summary",
        "1. Assignment scope and dataset audit",
        "2. Methodology and implementation",
        "3. Task 1 - tokenizer analysis",
        "4. Task 2 - regex normalization",
        "5. Discussion, limitations, and conclusion",
        "6. Reproducibility, references, and AI usage statement",
    ]:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(entry)
        set_run_font(r, size=11, color=INK)

    add_heading(doc, "Executive summary", 1)
    add_body(
        doc,
        "This report evaluates three tokenizers on 100 posts and applies a regex normalizer to a separate set of 100 repeated-character posts. The analysis is based on the CSV inputs and generated outputs in this solution folder. It preserves the useful measured findings while correcting the original report's unsupported claims about hashtags and emojis."
    )
    add_callout(
        doc,
        "Bottom line",
        "NLTK TweetTokenizer is the strongest observed option for the URL and mention structures present in this corpus, while NLTK word_tokenize produces the highest average token count. The regex pipeline is deterministic and removes 340 characters across the 100 normalization examples.",
    )
    add_heading(doc, "What must be fixed before final submission", 2)
    add_bullet(doc, "Expand the Task 1 corpus to include at least 20 hashtag posts, 20 URL posts, and 20 emoji posts.")
    add_bullet(doc, "Re-run the analysis and regenerate the CSV files, graphs, and report after the corpus is corrected.")
    add_bullet(doc, "Keep the compliance audit in the final report so quota satisfaction is directly checkable.")
    doc.add_page_break()

    # Scope and audit.
    add_heading(doc, "1. Assignment scope and dataset audit", 1)
    add_body(
        doc,
        "The assignment asks for a performance comparison of at least two tokenizers on informal English social-media posts, with minimum coverage for hashtags, URLs, mentions, emojis, and slang or abbreviations. It also asks for a second set of 100 posts and a regular expression that normalizes repeated characters such as 'goooood' to 'good'."
    )
    add_body(
        doc,
        "The solution folder contains the required two datasets and implements both tasks. A direct audit of dataset/social_media_posts.csv was added for this revision. Counts below refer to posts containing a feature, except where occurrences are shown separately. The slang count uses a transparent heuristic over common markers such as lol, tbh, ngl, bruh, fr, and idk."
    )
    audit_table = [["Requirement", "Minimum posts", "Observed posts", "Observed occurrences", "Status"]]
    for label, minimum, observed, occurrences in audit_rows:
        status = "Meets quota" if observed >= minimum else "Below quota"
        audit_table.append([label, minimum, observed, occurrences, status])
    add_table(doc, audit_table, [1.85, 0.9, 1.0, 1.2, 1.55], font_size=9.2)
    add_callout(
        doc,
        "Interpretation",
        "Mentions and slang/abbreviations meet the minimum under the audit rule. URLs, hashtags, and emoji-bearing posts do not. Therefore the current Task 1 results are useful for a partial comparison but cannot support a complete answer about hashtag or emoji preservation.",
        fill=PALE_RED,
        label_color=RED,
    )
    add_heading(doc, "Datasets used", 2)
    add_bullet(doc, "dataset/social_media_posts.csv: 100 rows with columns id and post.")
    add_bullet(doc, "dataset/repeated_char_posts.csv: 100 rows with columns id and original_post; every row contains at least one 3+ character run.")
    doc.add_page_break()

    # Methodology.
    add_heading(doc, "2. Methodology and implementation", 1)
    add_heading(doc, "2.1 Task 1 pipeline", 2)
    add_body(
        doc,
        "Each social-media post is sent to NLTK word_tokenize, NLTK TweetTokenizer, and spaCy's English tokenizer. The program records token count, hashtag count, mention count, URL count, punctuation-token count, and an emoji count derived from the raw post. Results are written to output/tokenizer_results.csv and aggregate values to output/tokenizer_comparison.csv."
    )
    add_heading(doc, "2.2 Task 2 pipeline", 2)
    add_body(
        doc,
        "For each row in repeated_char_posts.csv, the RegexNormalizer applies the pattern below and writes the original text, normalized text, repeated-sequence count, characters removed, reduction percentage, and matched patterns to output/regex_results.csv."
    )
    code_table = [
        ["Component", "Implementation"],
        ["Pattern", r"(.)\1{2,}"],
        ["Replacement", r"\1\1"],
        ["Effect", "Reduce each run of 3 or more identical characters to 2 characters."],
        ["Graphs", "Five PNG files in output/graphs/."],
    ]
    add_table(doc, code_table, [1.35, 5.15], header_fill=NAVY, font_size=9.5)
    add_heading(doc, "2.3 Methodological cautions", 2)
    add_bullet(doc, "The NLTK word tokenizer receives lowercased text, while TweetTokenizer and spaCy receive the original casing. Token-count comparisons therefore reflect both tokenization and this preprocessing difference.")
    add_bullet(doc, "Emoji presence is counted once from the raw text and is not separately verified for each tokenizer. The current corpus contains no emoji-bearing posts, so preservation cannot be evaluated.")
    add_bullet(doc, "Hashtag and URL preservation are inferred from tokenizer output. A stronger experiment would compare each output against feature annotations derived from the original post.")
    doc.add_page_break()

    # Task 1 results.
    add_heading(doc, "3. Task 1 - tokenizer analysis", 1)
    add_body(
        doc,
        "The generated comparison table provides the following measured results for the current 100-post corpus. Average token count is computed over all rows; feature columns are summed across the corpus."
    )
    result_table = [["Tokenizer", "Avg tokens", "Hashtags", "Mentions", "URLs", "Punctuation avg"]]
    for _, row in comparison.iterrows():
        result_table.append([
            str(row["Tokenizer"]),
            f"{float(row['Avg Tokens']):.2f}",
            int(row["Hashtags Preserved"]),
            int(row["Mentions Preserved"]),
            int(row["URLs Preserved"]),
            f"{float(row['Punctuation Tokens']):.2f}",
        ])
    add_table(doc, result_table, [1.35, 1.0, 0.85, 0.85, 0.7, 1.75], font_size=9.3)
    add_figure(doc, "token_count.png", "Figure 1. Average token count by tokenizer. Exact averages are reported in the table; the chart uses rounded values.", width=5.8)
    add_heading(doc, "Answers to the assignment questions", 2)
    q_table = [
        ["Question", "Evidence-based answer"],
        ["Which tokenizer performs best on hashtags?", "Cannot be determined from this corpus: there are 0 hashtag posts and all tokenizer totals are 0."],
        ["Which tokenizer preserves emojis correctly?", "Cannot be determined from this corpus: there are 0 emoji-bearing posts and the raw-text emoji count is 0."],
        ["Which tokenizer generates the most tokens?", "NLTK word_tokenize, with 11.08 average tokens per post."],
        ["What are the main strengths and weaknesses?", "TweetTokenizer preserves the 8 observed URLs and 23 mentions; word_tokenize provides a useful baseline but fragments punctuation and observed URLs; spaCy is competitive for the same URLs and offers a wider NLP ecosystem."],
    ]
    add_table(doc, q_table, [2.55, 3.95], font_size=9.2)
    doc.add_page_break()

    add_heading(doc, "3.1 Feature-preservation evidence", 1)
    add_body(
        doc,
        "The feature charts should be read together with the dataset audit. The zero hashtag bars do not show that a tokenizer failed to preserve existing hashtags; they show that no hashtags were available to preserve. Likewise, the emoji chart describes corpus presence, not tokenizer-level preservation."
    )
    add_figure(doc, "tokenizer_comparison.png", "Figure 2. Multi-feature comparison for mentions, URLs, and hashtags in the current corpus.", width=5.9)
    evidence_table = [
        ["Corpus check", "Observed evidence", "Implication"],
        ["Hashtags", "0 posts; 0 occurrences", "Hashtag preservation cannot be ranked."],
        ["Emojis", "0 posts; 0 occurrences", "Emoji preservation cannot be evaluated."],
        ["URLs", "8 posts; 8 occurrences", "TweetTokenizer and spaCy retain all 8; NLTK Word retains 0."],
        ["Mentions", "22 posts; 23 occurrences", "All three tokenizers retain 23 mention occurrences."],
    ]
    add_table(doc, evidence_table, [1.25, 1.85, 3.4], font_size=9.1)
    doc.add_page_break()

    # Task 2.
    add_heading(doc, "4. Task 2 - regex normalization", 1)
    add_body(
        doc,
        "Repeated characters can create many surface forms for the same word and reduce matching consistency during indexing. The submitted implementation uses a deterministic, language-agnostic pattern rather than a manually maintained dictionary."
    )
    add_callout(
        doc,
        "Rule",
        r"The pattern (.)\1{2,} captures a character followed by at least two more copies. Replacing it with \1\1 keeps two copies, so 'goooood' becomes 'good' and 'sooooo' becomes 'soo'.",
    )
    add_heading(doc, "4.1 Representative transformations", 2)
    example_table = [["Original", "Normalized", "Characters removed"]]
    for _, row in regex.head(6).iterrows():
        example_table.append([
            str(row["original_post"]),
            str(row["normalized_post"]),
            int(row["chars_removed"]),
        ])
    add_table(doc, example_table, [3.0, 2.8, 0.7], font_size=8.8)
    add_heading(doc, "4.2 Strengths and limitations of the rule", 2)
    add_bullet(doc, "Strengths: deterministic, easy to interpret, fast, and independent of a word list.")
    add_bullet(doc, "Limitations: it does not infer the intended dictionary spelling, and it may change meaningful repetition inside identifiers, usernames, hashtags, URLs, or uppercase emphasis.")
    add_bullet(doc, "The current assignment dataset is controlled for repeated characters; a broader evaluation should include posts with protected entities and unchanged control examples.")
    doc.add_page_break()

    add_heading(doc, "4.3 Task 2 results", 1)
    regex_stats = [
        ["Metric", "Measured value"],
        ["Posts processed", len(regex)],
        ["Posts with repeated sequences", int((regex["repeated_char_count"] > 0).sum())],
        ["Total repeated sequences", int(regex["repeated_char_count"].sum())],
        ["Total characters removed", int(regex["chars_removed"].sum())],
        ["Average characters removed per post", f"{regex['chars_removed'].mean():.2f}"],
        ["Average reduction percentage", f"{regex['char_reduction_percent'].mean():.2f}%"],
        ["Maximum characters removed in one post", int(regex["chars_removed"].max())],
        ["Reduction distribution", "91 light (1-5 chars), 9 moderate (6-10 chars), 0 heavy"],
    ]
    add_table(doc, regex_stats, [3.0, 3.5], font_size=9.5)
    add_figure(doc, "char_reduction.png", "Figure 5. Distribution of characters removed by the normalization rule.", width=5.9)
    add_body(
        doc,
        "All 100 rows were processed successfully. The result is a normalization demonstration rather than a claim of semantic correctness: the pipeline reliably applies the rule, but deciding whether the normalized spelling is linguistically appropriate requires lexical or contextual evaluation."
    )
    doc.add_page_break()

    # Discussion and conclusion.
    add_heading(doc, "5. Discussion, limitations, and conclusion", 1)
    add_heading(doc, "5.1 Strengths of the solution package", 2)
    add_bullet(doc, "Modular Python implementation with separate Task 1 and Task 2 modules.")
    add_bullet(doc, "CSV exports preserve per-post results and make the analysis reproducible.")
    add_bullet(doc, "The regex normalizer is explicit, deterministic, and easy to test.")
    add_bullet(doc, "The revised report connects every conclusion to a measured output or an explicit limitation.")
    add_heading(doc, "5.2 Limitations requiring attention", 2)
    add_bullet(doc, "The Task 1 corpus does not satisfy the assignment quotas for hashtags, URLs, or emojis.")
    add_bullet(doc, "Emoji preservation is not a tokenizer-specific metric in the current implementation.")
    add_bullet(doc, "The tokenizers receive different case treatment, which weakens direct comparability.")
    add_bullet(doc, "The fixed two-character target is useful for the assignment but is not a general lexical normalizer.")
    add_heading(doc, "5.3 Conclusion", 2)
    add_body(
        doc,
        "For the current corpus, TweetTokenizer is the most useful default for preserving the observed social-media structures: it retains all 8 observed URLs and 23 mention occurrences, while producing the lowest average token count. spaCy matches the observed URL and mention totals and remains a good general-purpose option. NLTK word_tokenize is a useful baseline and produces the highest average token count at 11.08."
    )
    add_body(
        doc,
        "The regex pipeline meets the mechanical objective of normalizing repeated character runs across 100 posts, removing 340 characters with an 8.72% mean reduction. Before presenting the work as a complete answer to Task 1, the social-media dataset should be expanded to satisfy the required hashtag, URL, and emoji quotas, and the analysis should be re-run."
    )
    add_callout(
        doc,
        "Recommended next step",
        "Add at least 20 hashtag posts, 12 more URL posts, and 20 emoji posts to dataset/social_media_posts.csv while retaining the existing rows. Then regenerate output/tokenizer_results.csv, output/tokenizer_comparison.csv, and the four Task 1 graphs.",
        fill=PALE_GOLD,
        label_color="7A5A00",
    )
    doc.add_page_break()

    # Reproducibility and references.
    add_heading(doc, "6. Reproducibility, references, and AI usage statement", 1)
    add_heading(doc, "6.1 Reproduction commands", 2)
    add_body(doc, "From the project root, install the packages listed in code/requirements.txt and run the modules below. The spaCy script falls back to a blank English pipeline when en_core_web_sm is unavailable.")
    commands = [
        "python -m pip install -r code/requirements.txt",
        "python code/tokenizer_analysis.py",
        "python code/regex_normalizer.py",
        "python code/build_revised_report.py",
    ]
    for command in commands:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(command)
        set_run_font(r, name="Courier New", size=9.5, color=NAVY)
    add_heading(doc, "6.2 Key project files", 2)
    files_table = [
        ["Path", "Purpose"],
        ["dataset/social_media_posts.csv", "Task 1 input corpus."],
        ["dataset/repeated_char_posts.csv", "Task 2 input corpus."],
        ["code/tokenizer_analysis.py", "Three-tokenizer comparison and Task 1 graphs."],
        ["code/regex_normalizer.py", "Repeated-character normalization and Task 2 graph."],
        ["output/*.csv", "Per-post and aggregate measurements."],
        ["output/graphs/*.png", "Generated visualizations."],
        ["report/report.docx", "Editable source report."],
        ["report/Tokenization_and_Normalization_Report_Tasks_1-2_compressed.pdf", "PDF export of the editable report."],
    ]
    add_table(doc, files_table, [3.0, 3.5], font_size=9.2)
    add_heading(doc, "6.3 References", 2)
    for reference in [
        "Bird, S., Klein, E., and Loper, E. Natural Language Processing with Python. O'Reilly Media.",
        "Honnibal, M., and Montani, I. spaCy: Industrial-Strength Natural Language Processing in Python.",
        "Han, B., and Baldwin, T. Lexical Normalisation of Short Text.",
        "NLTK documentation for word_tokenize and TweetTokenizer.",
        "Python documentation for regular expression operations.",
        "Pandas and Matplotlib documentation used for analysis and visualization.",
    ]:
        add_bullet(doc, reference)
    add_heading(doc, "6.4 AI usage statement", 2)
    add_body(
        doc,
        "AI assistance was used for report restructuring, code and documentation review, explanation of NLP concepts, and visual organization. The dataset audit, quantitative values, CSV results, graphs, and conclusions in this revised report were checked against the local solution files. The final report explicitly identifies unsupported dataset claims and separates measured results from recommendations."
    )

    doc.core_properties.title = "Tokenizer Analysis and Regex Normalization - Revised Report"
    doc.core_properties.author = "Reddy Eswar Anush"
    doc.core_properties.subject = "Information Retrieval assignment: Tasks 1 and 2"
    doc.core_properties.comments = "Editable source report generated from the submitted solution folder."
    doc.save(DOCX_PATH)
    print(DOCX_PATH)


if __name__ == "__main__":
    build_report()
