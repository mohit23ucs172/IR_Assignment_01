# Information Retrieval Assignment

This project contains two text-processing experiments for informal social-media text:

1. **Task 1 - Tokenizer analysis:** compare NLTK `word_tokenize`, NLTK `TweetTokenizer`, and spaCy.
2. **Task 2 - Regex normalization:** reduce runs of repeated characters such as `goooood` to `good`.

The revised report is evidence-based: it reports the values produced by the files in this folder and explicitly records where the current dataset does not meet the assignment brief.

## Current status

Task 2 is complete for its 100-row controlled dataset. Task 1 runs successfully, but its social-media corpus needs more feature coverage before it can be presented as a fully compliant submission.

| Assignment requirement | Minimum posts | Observed in `dataset/social_media_posts.csv` | Status |
|---|---:|---:|---|
| Hashtags | 20 | 0 | Not met |
| URLs | 20 | 8 | Not met |
| Mentions | 20 | 22 posts / 23 occurrences | Met |
| Emojis | 20 | 0 | Not met |
| Slang or abbreviations | 20 | 51 posts under the audit heuristic | Met |

The slang count uses common markers such as `lol`, `tbh`, `ngl`, `bruh`, `fr`, and `idk`. Counts above are a dataset audit, not a claim that the tokenizer output is correct.

## Project structure

```text
dataset/
  social_media_posts.csv          Task 1 input: 100 posts
  repeated_char_posts.csv         Task 2 input: 100 posts

code/
  main.py                         Interactive menu
  tokenizer_analysis.py           Task 1 analysis and four graphs
  regex_normalizer.py             Task 2 normalization and graph
  utils.py                        Shared CSV, table, timing, and graph helpers
  build_revised_report.py         Builds the editable report/report.docx
  requirements.txt                Python dependencies

output/
  tokenizer_results.csv           Per-post Task 1 measurements
  tokenizer_comparison.csv        Aggregate Task 1 comparison
  regex_results.csv               Per-post Task 2 measurements
  graphs/*.png                    Generated visualizations

report/
  report.docx                     Editable report source
  Tokenization_and_Normalization_Report_Tasks_1-2_compressed.pdf
                                  Text-based PDF export of report.docx
```

## Setup

Use Python 3.8 or newer.

```bash
python -m pip install -r code/requirements.txt
```

The tokenizer script downloads NLTK punkt data when needed. spaCy uses `en_core_web_sm` when it is installed and falls back to a blank English tokenizer when it is not. For the trained model, run:

```bash
python -m spacy download en_core_web_sm
```

## Run the analyses

From the project root:

```bash
python code/tokenizer_analysis.py
python code/regex_normalizer.py
```

Or launch the menu-driven interface:

```bash
python code/main.py
```

The scripts overwrite the CSV and graph files in `output/`.

## Rebuild the editable report

The Word document is the editable master. It is generated from the current CSV outputs and graphs:

```bash
python code/build_revised_report.py
```

After editing the DOCX, export it to PDF from Word or LibreOffice and keep the PDF beside it in `report/`. The PDF is text-based and selectable, but future content changes should be made in `report/report.docx` and then re-exported.

## Measured results in the current outputs

### Task 1

| Tokenizer | Average tokens | Hashtags | Mentions | URLs | Average punctuation tokens |
|---|---:|---:|---:|---:|---:|
| NLTK Word | 11.08 | 0 | 23 | 0 | 0.32 |
| NLTK Tweet | 10.63 | 0 | 23 | 8 | 0.00 |
| spaCy | 10.93 | 0 | 23 | 8 | 0.00 |

Interpretation:

- NLTK `word_tokenize` produces the highest average token count.
- TweetTokenizer and spaCy retain the 8 observed URLs; NLTK Word retains none under the project metric.
- All three tokenizers retain the 23 observed mention occurrences.
- Hashtag and emoji preservation cannot be ranked because the current corpus contains no hashtags or emojis.
- The implementation lowercases text only for NLTK Word, so token-count comparisons include a preprocessing difference.

### Task 2

- 100 posts processed; all 100 contain at least one repeated-character sequence.
- 133 repeated sequences found.
- 340 characters removed in total.
- 3.40 characters removed per post on average.
- 8.72% average character reduction.
- 91 posts had a light reduction of 1-5 characters; 9 had a moderate reduction of 6-10 characters.

The rule in `code/regex_normalizer.py` is:

```text
Pattern:     (.)\1{2,}
Replacement: \1\1
```

This keeps two copies of a repeated character. Therefore `goooood` becomes `good`, while `sooooo` becomes `soo`. The assignment's example shows `sooooo` becoming `so`; a one-copy replacement would be a different rule and should be documented and tested separately.

## Output files

Task 1 writes:

- `output/tokenizer_results.csv`
- `output/tokenizer_comparison.csv`
- `output/graphs/token_count.png`
- `output/graphs/emoji_preservation.png`
- `output/graphs/hashtag_analysis.png`
- `output/graphs/tokenizer_comparison.png`

Task 2 writes:

- `output/regex_results.csv`
- `output/graphs/char_reduction.png`

## Recommended pre-submission fix

Add rows to `dataset/social_media_posts.csv` while retaining the existing data:

- at least 20 posts containing hashtags;
- at least 12 additional URL posts, bringing the total to 20;
- at least 20 posts containing emojis.

Then rerun Task 1 and rebuild the report. The revised report already contains a compliance table so the final corpus can be checked directly.

## References and AI usage

The implementation uses NLTK, spaCy, pandas, Matplotlib, `emoji`, and Python regular expressions. The report references standard documentation and NLP literature for these tools and methods.

AI assistance was used for code and documentation review, report restructuring, NLP explanation, and layout organization. Local datasets, analysis outputs, graphs, quantitative values, and the dataset compliance audit were checked against the files in this folder.

## Author

Mohit Tiwari

Enrollment No.: 23UCS172

Registration No.: 2317020

Section: B
