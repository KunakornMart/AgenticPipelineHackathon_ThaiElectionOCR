# Super AI Engineer S6 – Thai Election OCR Challenge

> OCR and Vision LLM pipeline for extracting vote counts from scanned Thai election result documents in **Super AI Engineer Season 6 – Agentic Pipeline Hackathon / 2026 Thai Election OCR**.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![OCR](https://img.shields.io/badge/OCR-Thai%20Election%20Documents-529EFF)
![Vision LLM](https://img.shields.io/badge/Vision%20LLM-Gemini%20%2F%20OCR-9B7DF8)
![Computer Vision](https://img.shields.io/badge/Computer%20Vision-Table%20Extraction-2EC866)
![Metric](https://img.shields.io/badge/Metric-Mean%20Levenshtein%20Distance-EDB227)

---

## Highlights

| Item | Result |
|---|---:|
| Competition | **Super AI Engineer Season 6 – Thai Election OCR Challenge** |
| Hackathon Track | Agentic Pipeline Hackathon / 2026 Thai Election OCR |
| Task | OCR / Document AI / Thai vote-count extraction |
| Dataset Scale | 300 documents · 846 PNG page images · 10,053 submission rows |
| Evaluation Metric | Mean Levenshtein Distance |
| Result | **Rank 44** |
| Score | **Mean Levenshtein distance ≈ 0.2360** |
| Certificate | [Verify credential](https://mysuperai.aiat.or.th/certificate/hack2/600637) |

---

## Project Overview

This project extracts structured voting data from scanned Thai election result documents.

The input images are official-looking Thai election result forms, including:

- **Party-list result forms** containing party names and vote counts
- **Constituency result forms** containing candidate names, party names, and vote counts
- Multi-page scanned PNG documents
- Thai numerals and Thai text descriptions of vote counts

The target output is a CSV file with only two columns:

```csv
id,votes
```

Each `votes` value must be an Arabic-digit string or integer.

---

## Problem Statement

Given scanned Thai election result document images, the task is to:

1. Locate the correct table rows
2. Extract the corresponding vote count
3. Convert Thai numerals and Thai number words into Arabic digits
4. Align extracted values with the official submission template
5. Submit a valid `id,votes` CSV file

The task is challenging because the documents may contain:

- Thai digits, Arabic digits, and Thai number words
- Scanned document noise
- Multi-page documents
- Table borders and signatures
- Rows with totals that should not be included as candidate/party rows
- Different layouts for party-list and constituency documents

---

## Repository Structure

```text
.
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── data/
│   └── README.md
├── notebooks/
│   └── thai_election_ocr_solution.ipynb
├── src/
│   ├── ocr_pipeline.py
│   ├── postprocess_votes.py
│   └── validate_submission.py
├── assets/
│   └── sample_images/
│       ├── party_list_34_11.png
│       ├── party_list_34_11_page2.png
│       ├── party_list_34_11_page3.png
│       ├── constituency_10_1.png
│       ├── constituency_10_1_page2.png
│       └── constituency_10_1_page3.png
├── docs/
│   └── linkedin_project_entry.md
└── results/
    └── README.md
```

---

## Folder Guide

| Path | Description |
|---|---|
| [`data/`](./data) | Place the official `submission_template_v4.csv` here. Full image dataset is intentionally not included. |
| [`notebooks/`](./notebooks) | Main Kaggle/Colab notebook used for OCR experiments and final pipeline execution. |
| [`src/ocr_pipeline.py`](./src/ocr_pipeline.py) | Cleaned pipeline skeleton for image loading, OCR/Vision LLM prompting, parsing, and submission generation. |
| [`src/postprocess_votes.py`](./src/postprocess_votes.py) | Thai numeral normalization, Thai number-word conversion, vote cleaning, and vote validation utilities. |
| [`src/validate_submission.py`](./src/validate_submission.py) | Submission format validation script. |
| [`assets/sample_images/`](./assets/sample_images) | Small set of sample document images for demonstration only. |
| [`docs/linkedin_project_entry.md`](./docs/linkedin_project_entry.md) | LinkedIn-ready project description. |

---

## Data Policy

The full competition dataset is **not included** in this repository because it is large.

Full dataset scale:

| Item | Count |
|---|---:|
| Documents | 300 |
| PNG page images | 846 |
| Submission rows | 10,053 |
| Approximate size | ~519 MB |

This repository includes only a few sample images for portfolio demonstration.

To reproduce the full pipeline, place the official competition files locally:

```text
data/
├── images/
│   ├── party_list_34_11.png
│   ├── party_list_34_11_page2.png
│   └── ...
└── submission_template_v4.csv
```

The `data/images/` folder is ignored by `.gitignore` to avoid committing hundreds of large PNG files.

---

## Methodology

The solution uses a practical OCR + Vision LLM pipeline.

```text
Scanned PNG pages
   ↓
Image loading
   ↓
Table region detection / vote-column cropping
   ↓
Image enhancement
   ↓
Vision LLM OCR prompt
   ↓
JSON row extraction
   ↓
Thai digit and Thai number-word normalization
   ↓
Row alignment with submission template
   ↓
Submission validation
   ↓
id,votes CSV
```

---

## Core Pipeline

### 1. Image Loading

Each document can contain multiple page images.

Example naming pattern:

```text
party_list_34_11.png
party_list_34_11_page2.png
party_list_34_11_page3.png
constituency_10_1.png
constituency_10_1_page2.png
```

The pipeline groups pages by `doc_id` and processes all available pages for the same document.

---

### 2. Table and Vote-Column Cropping

The pipeline uses computer vision preprocessing to identify table regions and isolate the vote-count column.

Typical operations include:

- Grayscale conversion
- Adaptive thresholding
- Morphological line extraction
- Table bounding-box detection
- Vote-column crop generation
- Full-table crop fallback

This reduces OCR noise and helps the Vision LLM focus on the vote column.

---

### 3. Image Enhancement

The extracted vote-column crop is enhanced before OCR.

Enhancement steps may include:

- Resizing small crops
- CLAHE contrast enhancement
- Denoising
- Sharpening
- Normalization for Vision LLM input

This improves readability of Thai digits and Thai number words.

---

### 4. Vision LLM Prompting

The OCR prompt instructs the model to extract only the vote-count column.

The expected JSON structure:

```json
{
  "rows": [
    {"d": "๓๔,๑๗๗", "w": "สามหมื่นสี่พันหนึ่งร้อยเจ็ดสิบเจ็ด"},
    {"d": "๑๔,๘๑๓", "w": "หนึ่งหมื่นสี่พันแปดร้อยสิบสาม"}
  ],
  "bottom_total": {"d": "๗๗,๐๗๕", "w": "เจ็ดหมื่นเจ็ดพันเจ็ดสิบห้า"},
  "notes": []
}
```

The pipeline asks for both:

- `d`: visible numeric vote count
- `w`: Thai text in parentheses

If `d` and `w` disagree, the pipeline can choose the more reliable interpretation based on post-processing rules.

---

### 5. Thai Vote Normalization

Vote counts can appear as:

- Thai digits: `๑๔,๘๑๓`
- Arabic digits: `14,813`
- Thai number words: `หนึ่งหมื่นสี่พันแปดร้อยสิบสาม`
- Mixed/noisy OCR text

The post-processing module converts them into Arabic digits:

```text
๑๔,๘๑๓ → 14813
หนึ่งหมื่นสี่พันแปดร้อยสิบสาม → 14813
```

---

### 6. Row Alignment

The official template provides the expected submission IDs and row order.

The pipeline maps extracted vote counts back to:

```csv
id,votes
```

Important rules:

- Do not change `id`
- Submit all required rows
- Use Arabic digits only
- Do not include `party_name` in the final submission

---

### 7. Submission Validation

The validation script checks:

- Required columns: `id,votes`
- No missing IDs
- No duplicated IDs
- All votes are Arabic digits
- Optional row-count comparison against `submission_template_v4.csv`

Run:

```bash
python src/validate_submission.py results/submission.csv --template data/submission_template_v4.csv
```

---

## How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/KunakornMart/AgenticPipelineHackathon_ThaiElectionOCR.git
cd AgenticPipelineHackathon_ThaiElectionOCR
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare Data Locally

Place the official competition files locally:

```text
data/
├── images/
└── submission_template_v4.csv
```

Do not commit `data/images/` to GitHub.

### 4. Configure API Key

If using Gemini or a Vision LLM API, create a local `.env` file:

```bash
GEMINI_API_KEY=your_api_key_here
```

Never commit `.env` to GitHub.

### 5. Run Notebook

Open:

```text
notebooks/thai_election_ocr_solution.ipynb
```

Then run the notebook step by step.

### 6. Validate Submission

```bash
python src/validate_submission.py results/submission.csv --template data/submission_template_v4.csv
```

---

## Requirements

Main libraries:

- `pandas`
- `numpy`
- `opencv-python`
- `Pillow`
- `tqdm`
- `google-genai`
- `python-dotenv`
- `rapidfuzz`

Install:

```bash
pip install -r requirements.txt
```

---

## Skills Demonstrated

- OCR
- Computer Vision
- Vision Language Models
- Prompt Engineering
- Thai Document Processing
- Thai numeral normalization
- Thai number-word conversion
- Table extraction
- Data validation
- Competition pipeline design
- Python
- Kaggle workflow

---

## Key Takeaways

This project demonstrates how OCR and Vision LLMs can be combined with deterministic post-processing to extract structured data from noisy Thai scanned documents.

The main challenge was not only reading the document, but also:

- Locating the correct row
- Reading Thai vote-count text accurately
- Handling multi-page documents
- Aligning OCR results with the official template
- Validating the final submission format

This type of workflow is directly relevant to real-world document AI systems, especially for Thai forms, scanned reports, and structured document extraction tasks.

---

## LinkedIn Project Description

Built an OCR and Vision LLM pipeline to extract vote counts from scanned Thai election result documents. The task involved locating party or candidate rows, extracting vote counts, converting Thai numerals and Thai number words to Arabic digits, and validating outputs for 10,053 submission rows across 846 scanned page images.

Ranked **44th** with a mean Levenshtein distance of approximately **0.2360**.

---

## Certificate

Agentic Pipeline / Thai Election OCR Hackathon Certificate:  
https://mysuperai.aiat.or.th/certificate/hack2/600637

---

## Author

**Kunakorn Pruksakorn**  
Automation Engineer · Data Science · AI / LLM / OCR · Industrial IoT

- GitHub: [KunakornMart](https://github.com/KunakornMart)
- Portfolio: [kunakornmart.github.io](https://kunakornmart.github.io)
- LinkedIn: [Kunakorn Pruksakorn](https://linkedin.com/in/kunakorn-pruksakorn)

---

## License

This repository is provided for portfolio and educational purposes.

Dataset license follows the original competition dataset license.
