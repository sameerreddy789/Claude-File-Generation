# Claude File Generation & Compiler

This repository contains scripts and utilities for generating structured, beautifully formatted documents (like PDFs or DOCX files) from code templates, with a focus on automation and self-debugging.

## 🛠️ The Automated Compiler (`compile_script.py`)

When generating complex documents (such as ReportLab PDFs) using LLMs like Claude, the generated code often contains common layout or parameter errors, as well as hardcoded paths that don't match your local environment.

`compile_script.py` is a utility that automates the debugging and execution of these scripts.

### Key Features:
* 📂 **Output Path Redirection:** Automatically parses file generation paths (like `/mnt/user-data/outputs/...`) and redirects them to save directly within your local workspace directory.
* 🔧 **ReportLab Parameter Patching:** Swaps mismatched arguments in table styling functions (e.g. `LINEBEFORE`, `LINEAFTER`, `GRID`, etc.) from `(color, thickness)` back to ReportLab's expected `(thickness, color)` order.
* 🧼 **Invalid Border Cleanup:** Automatically removes invalid border tuples like `('LINEAFTER', ..., False)` which raise ValueErrors.
* 🐒 **Monkey-patched KeepTogether:** Injects a runtime patch into ReportLab's `KeepTogether` flowable to safely forward `setStyle` calls directly to the table inside, preventing crash-on-build issues.

---

## 🚀 How to Use

### 1. Installation & Setup
First, make sure your virtual environment is active and the dependencies are installed:

```bash
# Verify or install dependencies
.\.venv\Scripts\pip.exe install -r requirements.txt
```

### 2. Compile and Build a Document
To compile any generated Python script (e.g., a script that builds Anatomy notes) and generate its output:

```bash
.\.venv\Scripts\python.exe compile_script.py <path_to_script.py>
```

#### Example:
```bash
.\.venv\Scripts\python.exe compile_script.py generate_pdf.py
```
This will automatically patch all pathing and styling bugs in memory, execute the code, and save the output document directly in your folder!

---

## 📂 Repository Contents
* `compile_script.py`: The automated compiler and debugger utility.
* `generate_pdf.py`: A script that builds fully structured, color-coded Human Anatomy notes.
* `requirements.txt`: Project package dependencies (includes `reportlab`, `pillow`, etc.).
* `explore_doc.py`: Helper script to parse text and check layouts inside document templates.
