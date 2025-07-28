# Cisco\_Paypal\_Unemployed - Adobe Hackathon 2025 Round 1A Submission

## Team Members

* Ram Srikanth
* Nikhileshwar Reddy
* Thanush

---

## Project Overview

This solution intelligently derives structured outlines from PDF documents by examining textual layout features, such as font size, boldness, and spatial positioning. Our heading detection mechanism relies purely on rule-based heuristics—ensuring fast, lightweight performance without the need for pretrained models. The document title is extracted from either embedded metadata or inferred based on dominant visual styling from the first page. The pipeline is designed to run completely offline and is compatible with multilingual content.

---

## Technology Stack

* [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) — for efficient PDF text and layout extraction
* Python 3.11 — core programming language used

---

## Execution Instructions

### Build the Docker Image

```bash
docker build --platform linux/amd64 -t adobe-pdf-processor:ciscopaypal-v0 .
```

### Run the Docker Container

For Unix/macOS (Bash shell):

```bash
docker run --rm \
  -v $(pwd)/input:/input \
  -v $(pwd)/output:/output \
  --network none \
  adobe-pdf-processor:ciscopaypal-v0
```

For Windows PowerShell:

```powershell
docker run --rm `
  -v "${PWD}\input:/input" `
  -v "${PWD}\output:/output" `
  --network none `
  adobe-pdf-processor:ciscopaypal-v0
```

The container processes all `.pdf` files placed in the `/input` directory and generates their corresponding `.json` files in the `/output` directory.

---

## Output Specification

Each processed PDF results in a JSON file with the following structure:

```json
{
  "title": "Extracted Title",
  "outline": [
    { "level": "H1", "text": "Heading Text", "page": 1 },
    { "level": "H2", "text": "Subheading Text", "page": 2 }
  ]
}
```

---

## Compliance Checklist

* [x] Processes all valid PDF files in the input directory
* [x] Outputs a correctly formatted JSON per PDF
* [x] Adheres to the outline schema required by the challenge
* [x] Operates fully offline (no internet access required)
* [x] Completes execution within 10 seconds for a 50-page file
* [x] Stays within the 16GB memory constraint
* [x] Fully compatible with AMD64 (x86\_64) systems

---

## Directory Layout

```
.
├── input/             # Folder containing input PDF files
├── output/            # Directory for saving output JSON files
├── main.py            # Core Python script for outline extraction
├── Dockerfile         # Docker container configuration
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

---

## Submission Statement

This repository is submitted as part of **Adobe Hackathon 2025 - Round 1A** by the team **Cisco\_Paypal\_Unemployed**.
