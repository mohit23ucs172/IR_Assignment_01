"""Create the final PDF report for Tasks 1 and 2."""

from pathlib import Path
from statistics import mean, median, pstdev

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
GRAPHS = OUTPUT / "graphs"
REPORT_PATH = ROOT.parent / "Tokenization_and_Normalization_Report_Tasks_1-2_compressed.pdf"
REPOSITORY_URL = "https://github.com/reddyeswaranush/ir_assignment"


def table(data, widths=None, header=True):
    result = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9aa4b2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold" if header else "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        style.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324d")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ]
        )
    result.setStyle(TableStyle(style))
    return result


def p(text, style):
    return Paragraph(text, style)


def build_report():
    tokenizer = pd.read_csv(OUTPUT / "tokenizer_results.csv")
    comparison = pd.read_csv(OUTPUT / "tokenizer_comparison.csv")
    regex = pd.read_csv(OUTPUT / "regex_results.csv")

    emoji_font = Path(r"C:\Windows\Fonts\seguisym.ttf")
    body_font = "Helvetica"
    if emoji_font.exists():
        pdfmetrics.registerFont(TTFont("SegoeEmoji", str(emoji_font)))
        body_font = "SegoeEmoji"

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BodyJustified",
            parent=styles["BodyText"],
            fontName=body_font,
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontSize=8,
            leading=10,
            alignment=TA_JUSTIFY,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CenterTitle",
            parent=styles["Title"],
            fontSize=23,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17324d"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="CenterSubtitle",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
        )
    )

    doc = SimpleDocTemplate(
        str(REPORT_PATH),
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.6 * inch,
        title="Tokenization and Normalization Report - Tasks 1 and 2",
        author="Reddy Eswar Anush",
    )
    story = []

    def heading(text, level=1):
        story.append(Paragraph(text, styles["Heading1" if level == 1 else "Heading2"]))
        story.append(Spacer(1, 5))

    def body(text):
        story.append(p(text, styles["BodyJustified"]))

    def figure(filename, caption, width=6.4 * inch):
        path = GRAPHS / filename
        if path.exists():
            image = Image(str(path), width=width, height=width * 0.55)
            story.append(image)
            story.append(p(caption, styles["Small"]))
            story.append(Spacer(1, 8))

    avg = {
        "NLTK Word": tokenizer["nltk_word_tokens"].mean(),
        "NLTK Tweet": tokenizer["nltk_tweet_tokens"].mean(),
        "spaCy": tokenizer["spacy_tokens"].mean(),
    }
    stats = [
        ["Metric", "Value"],
        ["Social-media posts evaluated", str(len(tokenizer))],
        ["Repeated-character posts evaluated", str(len(regex))],
        ["Tokenizers compared", "3"],
        ["Total characters removed in Task 2", str(int(regex["chars_removed"].sum()))],
        ["Average reduction per post", f"{regex['chars_removed'].mean():.2f} characters"],
        ["Average reduction percentage", f"{regex['char_reduction_percent'].mean():.2f}%"],
        ["Repository", REPOSITORY_URL],
    ]

    story += [
        Spacer(1, 1.1 * inch),
        p("INFORMATION RETRIEVAL & NLP PROJECT", styles["CenterTitle"]),
        Spacer(1, 0.25 * inch),
        p("Tasks 1-2: Tokenization and Text Normalization", styles["CenterSubtitle"]),
        Spacer(1, 0.25 * inch),
        p("for Informal Social-Media Text", styles["CenterSubtitle"]),
        Spacer(1, 0.4 * inch),
        table(
            [
                ["★ TASK 1", "✦ TASK 2", "✓ OUTPUT"],
                ["Tokenizer analysis", "Regex cleanup", "Charts + tables"],
            ],
            widths=[2.05 * inch, 2.05 * inch, 2.05 * inch],
        ),
        Spacer(1, 0.35 * inch),
        p("Submitted by", styles["BodyText"]),
        p("<b>Reddy Eswar Anush</b>", styles["CenterSubtitle"]),
        p("Enrollment No.: 23UCS173<br/>Registration No.: 2317023<br/>Section: B", styles["BodyText"]),
        Spacer(1, 0.3 * inch),
        p("Information Retrieval Assignment", styles["BodyText"]),
        p("September 2026", styles["BodyText"]),
        Spacer(1, 0.25 * inch),
        p(f"GitHub Repository: {REPOSITORY_URL}", styles["Small"]),
        PageBreak(),
    ]

    heading("CONTENTS")
    for item in [
        "Part I - Task 1: Performance Analysis of Tokenization Tools",
        "1. Introduction and objectives",
        "2. Dataset and ground-truth features",
        "3. Tokenizers evaluated and methodology",
        "4. Task 1 results and discussion",
        "Part II - Task 2: Regex-Based Normalization",
        "5. Normalization objective and design",
        "6. Implementation and examples",
        "7. Error analysis, strengths, and limitations",
        "8. Conclusion and future work",
        "9. References and AI usage statement",
    ]:
        story.append(p(item, styles["BodyText"]))
    story += [PageBreak()]

    heading("PART I - TASK 1")
    story.append(p("Performance Analysis of Tokenization Tools on Informal English Social-Media Text", styles["CenterSubtitle"]))
    heading("1. Introduction and Objectives")
    body(
        "Tokenization converts raw text into units that can be indexed, counted, searched, or passed "
        "to later NLP components. Social-media text makes this step difficult because a single post may "
        "combine ordinary words with @mentions, #hashtags, URLs, emojis, abbreviations, repeated letters, "
        "and unconventional punctuation. A tokenizer that fragments these units may increase token counts "
        "while losing information needed for retrieval."
    )
    body(
        "The objective of Task 1 is therefore not simply to find the tokenizer producing the fewest or "
        "most tokens. It is to compare token granularity and the preservation of structures important to "
        "social-media retrieval. The experiment compares NLTK word_tokenize, NLTK TweetTokenizer, and "
        "spaCy's English tokenizer."
    )
    heading("2. Dataset and Ground-Truth Features")
    body(
        "The project dataset contains 100 realistic English social-media posts. The posts include mixed "
        "capitalization, informal spellings, slang and abbreviations, multiple emojis, hashtags, mentions, "
        "and realistic web links. Ground-truth counts for hashtags, mentions, URLs, and emojis are derived "
        "from the original post before tokenizer output is inspected. This avoids defining correctness from "
        "the output of any one tokenizer."
    )
    story.append(table(stats, widths=[2.6 * inch, 3.8 * inch]))
    story += [PageBreak()]

    heading("3. Tokenizers Evaluated and Methodology")
    body(
        "<b>NLTK word_tokenize:</b> a conventional Penn Treebank-style tokenizer intended for ordinary "
        "written English. It commonly separates punctuation and may fragment URLs or social-media markers."
    )
    body(
        "<b>NLTK TweetTokenizer:</b> a tokenizer designed for tweet-like text. It is expected to keep "
        "mentions, hashtags, URLs, and informal constructions together more often than a general tokenizer."
    )
    body(
        "<b>spaCy:</b> a production-oriented English tokenizer with configurable special cases and a "
        "broader NLP ecosystem. In this project it uses the available English pipeline, with a blank English "
        "pipeline as a fallback when the trained model is unavailable."
    )
    body(
        "For every post, the program records token count, hashtag count, mention count, URL count, "
        "punctuation-token count, and emoji count. Processing time is measured around the analysis loop. "
        "Results are written to tokenizer_results.csv and the aggregate comparison is written to "
        "tokenizer_comparison.csv."
    )
    heading("4. Task 1 Results and Discussion")
    comparison_data = [["Tokenizer", "Average tokens", "Hashtags", "Mentions", "URLs", "Punctuation"]]
    for _, row in comparison.iterrows():
        comparison_data.append(
            [
                str(row["Tokenizer"]),
                f"{float(row['Avg Tokens']):.2f}",
                str(int(row["Hashtags Preserved"])),
                str(int(row["Mentions Preserved"])),
                str(int(row["URLs Preserved"])),
                f"{float(row['Punctuation Tokens']):.2f}",
            ]
        )
    story.append(table(comparison_data, widths=[1.35 * inch, 1.0 * inch, 0.85 * inch, 0.8 * inch, 0.65 * inch, 1.0 * inch]))
    story.append(Spacer(1, 10))
    body(
        "The comparison shows that token count is a measure of segmentation rather than a direct quality "
        "score. The TweetTokenizer produces the lowest average token count in this dataset and preserves "
        "the social-media structures that are represented in the CSV. spaCy is competitive for URLs and "
        "general text processing, while word_tokenize is more likely to split punctuation and structured "
        "social-media text. The best choice depends on the downstream retrieval task: TweetTokenizer is "
        "the strongest default for preserving tweet-like units, whereas spaCy is useful when tokenization "
        "will be followed by broader linguistic analysis."
    )
    figure("token_count.png", "Figure 1. Average token count produced by the three tokenizers.")
    body("★ <b>Chart reading:</b> token count measures segmentation. The strongest tokenizer is the one that keeps meaningful social-media units intact, not simply the one with the fewest tokens.")
    figure("hashtag_analysis.png", "Figure 2. Hashtag preservation comparison.")
    body("◆ <b>Hashtag insight:</b> complete hashtag tokens remain searchable as topic markers, which is valuable for indexing and topic-based retrieval.")
    figure("emoji_preservation.png", "Figure 3. Emoji presence in the evaluated corpus.")
    body("☺ <b>Emoji insight:</b> emojis carry sentiment and emphasis, so preserving them helps retain expressive information from informal posts.")
    story += [PageBreak()]

    heading("PART II - TASK 2")
    story.append(p("Regex-Based Normalization of Repeated Characters in Social-Media Posts", styles["CenterSubtitle"]))
    heading("5. Normalization Objective and Design")
    body(
        "Repeated characters are common in informal posts because writers use them to express emphasis "
        "or emotion: <i>goooood</i>, <i>sooooo</i>, <i>nooooo</i>, and <i>happppyyyyy</i>. Such variation "
        "increases vocabulary sparsity and can reduce matching consistency during indexing. Task 2 uses a "
        "deterministic regular-expression pipeline rather than a manually coded list of words."
    )
    body(
        "The core pattern is <font name='Courier'>(.)\\1{2,}</font>. The first group captures one character "
        "and the back-reference identifies two or more additional copies. The replacement "
        "<font name='Courier'>\\1\\1</font> keeps two copies. Thus, a run of three or more identical "
        "characters is reduced to a double character while ordinary single and double characters remain unchanged."
    )
    heading("6. Implementation and Examples")
    body(
        "The RegexNormalizer class loads repeated_char_posts.csv, applies the pattern to each original_post, "
        "counts matched groups, calculates characters removed and percentage reduction, and stores the original "
        "and normalized text in regex_results.csv. The implementation is language-agnostic and does not "
        "manually replace individual words."
    )
    examples = [["Original", "Normalized", "Interpretation"]]
    for _, row in regex.head(6).iterrows():
        examples.append([row["original_post"][:42], row["normalized_post"][:42], f"{int(row['chars_removed'])} chars removed"])
    story.append(table(examples, widths=[2.35 * inch, 2.35 * inch, 1.65 * inch]))
    story.append(Spacer(1, 10))
    figure("char_reduction.png", "Figure 4. Distribution of characters removed by normalization.")
    body("✦ <b>Normalization insight:</b> most posts need only a small reduction, showing that the regex removes expressive noise while keeping the message readable.")
    heading("7. Error Analysis, Strengths, and Limitations")
    body(
        "The rule is effective for expressive spelling variation, but a generic repetition rule cannot infer "
        "the writer's intended lexical form. Keeping two characters preserves some emphasis, yet it may not "
        "produce the dictionary spelling in every case. Runs inside identifiers, usernames, hashtags, URLs, "
        "stock symbols, or uppercase emphasis may be meaningful and should be protected in a more advanced "
        "pipeline. The current assignment intentionally demonstrates the core regex requirement on a controlled "
        "dataset."
    )
    body(
        "Strengths include deterministic output, linear-time processing, simple implementation, and easy "
        "interpretability. Limitations include the fixed two-character target, lack of lexical correction, "
        "and the absence of explicit entity protection. These limitations also define clear directions for "
        "future improvement."
    )
    figure("tokenizer_comparison.png", "Figure 5. Multi-feature comparison across tokenizers.")
    body("✓ <b>Overall comparison:</b> TweetTokenizer is strongest for social-media markers, while spaCy is useful when broader linguistic processing is needed.")
    story += [PageBreak()]

    heading("8. Conclusion and Future Work")
    body(
        "This project demonstrates that preprocessing choices affect how informal social-media posts are "
        "represented for information retrieval. NLTK TweetTokenizer is the most suitable of the tested "
        "tokenizers when hashtags, mentions, URLs, and informal text need to remain recognizable. spaCy "
        "offers a strong general-purpose alternative, while conventional word_tokenize provides a useful "
        "baseline but fragments more social-media structures."
    )
    body(
        "The regex pipeline successfully reduces repeated-character noise across all 100 Task 2 posts. "
        f"It removed {int(regex['chars_removed'].sum())} characters in total and achieved an average reduction "
        f"of {regex['char_reduction_percent'].mean():.2f}%. Future work should protect URLs, mentions, "
        "hashtags, and cashtags before normalization; add lexical lookup for selecting one or two characters; "
        "evaluate more tokenizers such as BERT or SentencePiece; and measure the effect on retrieval precision "
        "and recall."
    )
    heading("9. References")
    for reference in [
        "Bird, S., Klein, E., and Loper, E. Natural Language Processing with Python. O'Reilly Media.",
        "Honnibal, M., and Montani, I. spaCy: Industrial-Strength Natural Language Processing in Python.",
        "Han, B., and Baldwin, T. Lexical Normalisation of Short Text.",
        "NLTK Documentation: Tokenization and TweetTokenizer.",
        "Python Documentation: Regular Expression Operations.",
        "Matplotlib and pandas documentation used for analysis and visualization.",
    ]:
        story.append(p(reference, styles["BodyText"]))
    heading("AI Usage Statement")
    body(
        "AI assistance was used for coding support, report structuring, explanation of NLP concepts, "
        "debugging guidance, and review of implementation choices. Dataset generation, local execution, "
        "CSV outputs, visualizations, and the quantitative observations in this report were produced from "
        "the submitted project files. The student reviewed and assembled the final work."
    )
    story += [PageBreak()]

    heading("APPENDIX: PROJECT STRUCTURE AND REPRODUCIBILITY")
    body(
        "The repository contains dataset files, modular Python source code, generated CSV results, graphs, "
        "and documentation. From the repository root, install dependencies with "
        "<font name='Courier'>pip install -r code/requirements.txt</font>. Run "
        "<font name='Courier'>python code/main.py</font> to access the menu, or run the two analysis modules "
        "directly. The final project is available at:"
    )
    story.append(p(REPOSITORY_URL, styles["CenterSubtitle"]))
    story.append(Spacer(1, 12))
    story.append(table(stats, widths=[2.6 * inch, 3.8 * inch]))

    doc.build(story)


if __name__ == "__main__":
    build_report()
    print(REPORT_PATH)
