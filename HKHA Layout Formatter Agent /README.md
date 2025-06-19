# HKHA Layout Formatter Agent

> A FastAPI-based agent to automate and standardize document layout for the Hong Kong Hospital Authority (HKHA) publishing system, ensuring consistent styling, faster turnaround, and error-free output.

---

## Introduction

The **HKHA Layout Formatter Agent** streamlines the production of internal reports, newsletters, memos and forms by applying HKHA’s corporate design standards automatically. It replaces time-consuming manual typesetting with a reliable, API-driven workflow, reducing errors and accelerating publishing cycles.

---

## Key Features & Effects

| Feature                         | Description                                                                                      | Effect / Benefit                                                        |
|---------------------------------|--------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| **Template-Based Styling**      | Predefined HKHA templates for headers, footers, fonts, colors and margins.                       | Instant brand consistency; no manual style adjustments.                |
| **Markdown & HTML Input**       | Accept raw Markdown or HTML content with simple API calls.                                       | Writers focus on content — formatting is fully automated.             |
| **Dynamic Table & Chart Injection** | Parse data placeholders and render tables or SVG charts in the document.                      | Data-driven sections always use up-to-date figures, no copy-paste.      |
| **Multi-Format Output**         | Generate PDF, styled HTML or back-converted Markdown.                                            | Flexible distribution: print-ready PDF, intranet HTML, or archivable MD.|
| **FastAPI Service**             | Expose `/format` and `/templates` endpoints for integration with CI/CD pipelines and UIs.        | On-demand or batch jobs; easy integration into existing workflows.    |
| **Error Handling & Validation** | Schema validation, template checks, and meaningful error messages.                                | Reduces formatting glitches; faster troubleshooting.                   |
| **Pluggable Pipeline**          | Separate modules (`data_process.py` for logic, `fastapi_version.py` for service).                 | Clear separation of concerns; easy to extend or swap components.       |

---

## Architecture

```text
┌───────────────┐     ┌──────────────────┐     ┌───────────────┐
│  Client Apps  │───▶│  FastAPI Server  │───▶│ Layout Engine │
│ (CLI/UI/CI)   │    │ (fastapi_version) │    │ (data_process)│
└───────────────┘    └──────────────────┘     └───────────────┘
         ▲                   │   ▲                   │
         │                   │   │                   ▼
         └─── Outputs: PDF, HTML, MD ─────────────────┘
````

---

## Installation

```bash
git clone https://github.com/agent-collection/hkha-layout-formatter-agent.git
cd hkha-layout-formatter-agent

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Usage

### 1. Start the API

```bash
uvicorn fastapi_version:app --reload --host 0.0.0.0 --port 8000
```

### 2. Submit a Format Request

```bash
curl -X POST http://localhost:8000/format \
  -H "Content-Type: application/json" \
  -d '{
        "template": "standard_report",
        "content": "# Patient Safety Report\n\nDetails go here...",
        "output_format": "pdf"
      }' \
  --output report.pdf
```

**Effect**: Instantly receive a print-ready PDF with HKHA styling applied.

---

## API Reference

### `POST /format`

Apply HKHA layout to your document.

* **Request Body**

  | Field           | Type     | Description                                           |
  | --------------- | -------- | ----------------------------------------------------- |
  | `template`      | `string` | Template name (e.g. `standard_report`, `newsletter`). |
  | `content`       | `string` | Markdown or HTML source.                              |
  | `output_format` | `string` | `pdf`, `html`, or `md`.                               |

* **Response**

  * **200 OK**: Binary file in requested format.
  * **400**: Validation errors.
  * **500**: Server errors.

### `GET /templates`

List available layout templates.

* **Response**

  ```json
  { "templates": ["standard_report", "newsletter", "memo"] }
  ```

---
