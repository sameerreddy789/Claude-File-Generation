const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, LevelFormat, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, PageBreak
} = require('docx');
const fs = require('fs');

// ── Color palette ──────────────────────────────────────────────
const BLUE       = "185FA5";  // accent
const BLUE_LIGHT = "E6F1FB";  // table header fill
const PURPLE     = "534AB7";  // layer 3
const TEAL       = "0F6E56";  // layer 2
const AMBER      = "854F0B";  // layer 4 agents
const RED        = "A32D2D";  // risk / attention
const GRAY_BG    = "F4F4F4";  // alternating rows
const WHITE      = "FFFFFF";

// ── Helpers ─────────────────────────────────────────────────────
const cell = (text, opts = {}) => new TableCell({
  borders: {
    top:    { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
    bottom: { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
    left:   { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
    right:  { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" },
  },
  shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR } : undefined,
  width:   opts.width ? { size: opts.width, type: WidthType.DXA } : undefined,
  margins: { top: 80, bottom: 80, left: 120, right: 120 },
  verticalAlign: VerticalAlign.CENTER,
  children: [new Paragraph({
    alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
    children: [new TextRun({
      text,
      bold: opts.bold || false,
      color: opts.color || "000000",
      size: opts.size || 20,
      font: "Arial",
    })]
  })]
});

const hrow = (cells) => new TableRow({
  tableHeader: true,
  children: cells
});

const row = (cells) => new TableRow({ children: cells });

const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  children: [new TextRun({ text, font: "Arial" })]
});

const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  children: [new TextRun({ text, font: "Arial" })]
});

const body = (text, opts = {}) => new Paragraph({
  spacing: { after: 160 },
  alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
  children: [new TextRun({
    text,
    font: "Arial",
    size: 20,
    bold: opts.bold || false,
    color: opts.color || "333333",
    italics: opts.italic || false,
  })]
});

const bullet = (text, ref = "bullets") => new Paragraph({
  numbering: { reference: ref, level: 0 },
  spacing: { after: 80 },
  children: [new TextRun({ text, font: "Arial", size: 20, color: "333333" })]
});

const spacer = () => new Paragraph({ spacing: { after: 240 }, children: [new TextRun("")] });

const divider = () => new Paragraph({
  spacing: { after: 160 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: BLUE, space: 1 } },
  children: [new TextRun("")]
});

// ── Tables ──────────────────────────────────────────────────────

function layerTable(layerName, color, rows_data) {
  const COL = [2880, 1800, 1440, 3240];  // sums to 9360
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: COL,
    rows: [
      hrow([
        cell("Tool / Library",    { fill: color, bold: true, color: WHITE, size: 20, width: COL[0] }),
        cell("Role",              { fill: color, bold: true, color: WHITE, size: 20, width: COL[1] }),
        cell("License",           { fill: color, bold: true, color: WHITE, size: 20, width: COL[2] }),
        cell("Why chosen",        { fill: color, bold: true, color: WHITE, size: 20, width: COL[3] }),
      ]),
      ...rows_data.map((r, i) => row([
        cell(r[0], { fill: i % 2 === 0 ? WHITE : GRAY_BG, bold: true, size: 20, width: COL[0] }),
        cell(r[1], { fill: i % 2 === 0 ? WHITE : GRAY_BG, size: 20, width: COL[1] }),
        cell(r[2], { fill: i % 2 === 0 ? WHITE : GRAY_BG, size: 18, color: "666666", width: COL[2] }),
        cell(r[3], { fill: i % 2 === 0 ? WHITE : GRAY_BG, size: 20, width: COL[3] }),
      ]))
    ]
  });
}

function mockDataTable() {
  const COL = [2200, 2000, 1600, 3560];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: COL,
    rows: [
      hrow([
        cell("Document type",      { fill: BLUE, bold: true, color: WHITE, size: 20, width: COL[0] }),
        cell("Mock file format",   { fill: BLUE, bold: true, color: WHITE, size: 20, width: COL[1] }),
        cell("Entity types",       { fill: BLUE, bold: true, color: WHITE, size: 20, width: COL[2] }),
        cell("Compliance coverage",{ fill: BLUE, bold: true, color: WHITE, size: 20, width: COL[3] }),
      ]),
      row([cell("P&ID Diagram (mock)",         {fill:WHITE,  bold:true, width:COL[0]}), cell("PDF + scanned PNG", {fill:WHITE, width:COL[1]}),  cell("Equipment tags, pipe specs", {fill:WHITE, width:COL[2]}), cell("OISD-118 vessel inspection intervals",           {fill:WHITE, width:COL[3]})]),
      row([cell("SOP — Valve Isolation",        {fill:GRAY_BG,bold:true, width:COL[0]}), cell("DOCX",              {fill:GRAY_BG, width:COL[1]}), cell("Procedure steps, roles",    {fill:GRAY_BG, width:COL[2]}), cell("Factories Act §41G isolation lock-out",           {fill:GRAY_BG, width:COL[3]})]),
      row([cell("Maintenance Work Order #042", {fill:WHITE,  bold:true, width:COL[0]}), cell("CSV / XLSX",        {fill:WHITE, width:COL[1]}),   cell("Asset ID, failure mode",    {fill:WHITE, width:COL[2]}), cell("OEM service interval vs. actual date gap",       {fill:WHITE, width:COL[3]})]),
      row([cell("Annual Inspection Report",    {fill:GRAY_BG,bold:true, width:COL[0]}), cell("PDF (text-layer)",  {fill:GRAY_BG, width:COL[1]}), cell("Inspector, findings, date", {fill:GRAY_BG, width:COL[2]}), cell("PESO Form 17 certification gap detection",        {fill:GRAY_BG, width:COL[3]})]),
      row([cell("OISD-118 Regulation",         {fill:WHITE,  bold:true, width:COL[0]}), cell("PDF (scraped)",     {fill:WHITE, width:COL[1]}),   cell("Clause refs, thresholds",   {fill:WHITE, width:COL[2]}), cell("Clause-to-procedure mapping, gap evidence",      {fill:WHITE, width:COL[3]})]),
      row([cell("Incident Report #IR-2023-07", {fill:GRAY_BG,bold:true, width:COL[0]}), cell("JSON / email body",{fill:GRAY_BG, width:COL[1]}),  cell("Cause, equipment, severity",{fill:GRAY_BG, width:COL[2]}), cell("Lessons Learned feed for RCA agent context",     {fill:GRAY_BG, width:COL[3]})]),
    ]
  });
}

function evalTable() {
  const COL = [2400, 2160, 2400, 2400];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: COL,
    rows: [
      hrow([
        cell("Evaluation metric",        { fill: BLUE, bold: true, color: WHITE, size: 20, width: COL[0] }),
        cell("Target",                   { fill: BLUE, bold: true, color: WHITE, size: 20, width: COL[1] }),
        cell("How measured",             { fill: BLUE, bold: true, color: WHITE, size: 20, width: COL[2] }),
        cell("Tooling",                  { fill: BLUE, bold: true, color: WHITE, size: 20, width: COL[3] }),
      ]),
      row([cell("Entity extraction accuracy",   {fill:WHITE,   width:COL[0]}), cell(">85% F1 on mock corpus",   {fill:WHITE, width:COL[1]}),  cell("Manual annotation vs. GraphRAG output", {fill:WHITE, width:COL[2]}),  cell("Label Studio (open source)",     {fill:WHITE, width:COL[3]})]),
      row([cell("Compliance gap recall",         {fill:GRAY_BG, width:COL[0]}), cell(">90% gaps flagged",       {fill:GRAY_BG, width:COL[1]}), cell("Benchmark questions from OISD-118",     {fill:GRAY_BG, width:COL[2]}), cell("Manual judge + Claude API eval", {fill:GRAY_BG, width:COL[3]})]),
      row([cell("Query answer quality (RAG)",   {fill:WHITE,   width:COL[0]}), cell("RAGAS score >0.75",        {fill:WHITE, width:COL[1]}),  cell("RAGAS faithfulness + relevance",        {fill:WHITE, width:COL[2]}),  cell("RAGAS framework",                {fill:WHITE, width:COL[3]})]),
      row([cell("Time-to-answer vs. search",    {fill:GRAY_BG, width:COL[0]}), cell("<5 s vs. legacy 20+ min", {fill:GRAY_BG, width:COL[1]}), cell("Timed demo with reference question set",{fill:GRAY_BG, width:COL[2]}), cell("Stopwatch + demo script",       {fill:GRAY_BG, width:COL[3]})]),
      row([cell("Graph linkage completeness",   {fill:WHITE,   width:COL[0]}), cell(">80% cross-doc links",     {fill:WHITE, width:COL[1]}),  cell("Check equipment tag → SOP → reg links", {fill:WHITE, width:COL[2]}),  cell("Neo4j Cypher audit queries",     {fill:WHITE, width:COL[3]})]),
    ]
  });
}

// ── Document ─────────────────────────────────────────────────────
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 20, color: "333333" } } },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: BLUE },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "1a1a1a" },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 }
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Arial", color: "2a2a2a" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 }
      },
    ]
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
      {
        reference: "numbers",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1260, bottom: 1440, left: 1260 }
      }
    },
    children: [

      // ── COVER ──────────────────────────────────────────────────
      new Paragraph({ spacing: { after: 80 },  children: [new TextRun({ text: "Economic Times AI Hackathon 2026  ·  Problem Statement 8", font: "Arial", size: 18, color: "888888", italics: true })] }),
      new Paragraph({ spacing: { after: 320 }, children: [new TextRun({ text: "PlantBrain", font: "Arial", size: 72, bold: true, color: BLUE })] }),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Industrial Knowledge Intelligence Platform", font: "Arial", size: 32, bold: false, color: "333333" })] }),
      new Paragraph({ spacing: { after: 480 }, children: [new TextRun({ text: "Tech Stack Reference & Implementation Plan  ·  Compliance Intelligence Centerpiece", font: "Arial", size: 22, color: "666666", italics: true })] }),
      divider(),
      spacer(),

      // ── 1. PROBLEM ──────────────────────────────────────────────
      h1("1.  Problem we are solving"),
      body("Indian heavy industry plants operate across 7–12 disconnected document systems. Maintenance teams make critical decisions without access to complete equipment history, causing 18–22% of unplanned downtime events (BIS Research). The knowledge cliff — 25% of experienced engineers retiring this decade — makes the problem irreversible without AI-assisted knowledge capture."),
      body("PlantBrain addresses this by ingesting every heterogeneous document class into a unified knowledge graph, then deploying specialist AI agents to make that graph actionable. Our hackathon centrepiece is the Compliance Intelligence Engine — an agentic system that maps live regulatory requirements (OISD, PESO, Factories Act) against current equipment states, auto-generates audit evidence packages, and pushes gap alerts to field technicians on mobile."),
      spacer(),

      // ── 2. ARCHITECTURE OVERVIEW ────────────────────────────────
      h1("2.  Architecture overview (6 layers)"),
      body("The platform is a six-layer pipeline. Each layer is independently swappable, which matters for a hackathon where we may need to hot-swap a model or DB due to API limits."),
      spacer(),

      // Layer 1
      h2("Layer 1 — Document sources"),
      body("Heterogeneous input formats ingested as-is: P&IDs and engineering drawings (PDF/PNG/TIFF), maintenance work orders (XLSX/CSV), SOPs and safety procedures (DOCX/PDF), inspection and audit reports (PDF), email archives (EML/MSG), and regulatory standards (PDF scraped from BIS/OISD/PESO portals)."),
      spacer(),

      // Layer 2
      h2("Layer 2 — Document intelligence"),
      layerTable("Layer 2 — OCR / Layout / Vision", TEAL, [
        ["PaddleOCR v3",      "Text & table extraction",        "Apache 2.0",   "Best-in-class open-source OCR; handles scanned industrial forms, mixed Hindi/English labels, and dense table layouts natively"],
        ["Surya",             "Layout analysis + reading order","Apache 2.0",   "Fast modern layout detector; correctly orders multi-column SOPs and segments drawing title blocks from diagram bodies"],
        ["LayoutLMv3",        "P&ID multimodal parsing",        "CC BY-NC 4.0", "Combines text, layout coordinates, and image pixels; identifies instrument tags, pipe specs, and equipment annotations in P&ID sheets"],
        ["Unstructured.io",   "Email / XLSX / MSG parsing",     "Apache 2.0",   "Handles the awkward formats OCR can't — embedded Excel tables in emails, mixed binary attachments — with a unified output schema"],
      ]),
      spacer(),

      // Layer 3
      h2("Layer 3 — Knowledge graph & vector store"),
      layerTable("Layer 3 — Graph & Retrieval", PURPLE, [
        ["Microsoft GraphRAG","Entity + community graph build", "MIT",          "Converts raw text chunks into a knowledge graph with LLM-extracted entities and relationships; community clustering enables global summary queries across the full corpus"],
        ["OntoGPT",           "Industrial ontology alignment",  "MIT",          "Schema-driven extraction against ISO 15926 / CFIHOS; ensures equipment tags, process parameters, and regulatory references are typed consistently across document sources"],
        ["LlamaIndex KG",     "Graph query interface",          "MIT",          "Provides a clean abstraction for hybrid graph+vector queries; used to retrieve sub-graph context alongside dense vector hits for the compliance agent"],
        ["Neo4j Community",   "Primary graph database",         "GPL 3.0",      "Native graph storage for entities (Equipment, Procedure, Regulation, WorkOrder, Inspection) and their relationships; Cypher queries power cross-document linking"],
        ["Qdrant",            "Vector store + metadata filters","Apache 2.0",   "Dense vector search with payload filtering (by asset ID, document type, date range); enables the compliance agent to retrieve only relevant equipment-specific chunks"],
      ]),
      spacer(),

      // Layer 4
      h2("Layer 4 — Multi-agent orchestration"),
      layerTable("Layer 4 — Agent Runtime", AMBER, [
        ["LangGraph",         "Stateful orchestrator (hub)",    "MIT",          "Cyclic graph runtime that routes queries to specialist agents, manages shared state across agent turns, and supports human-in-the-loop checkpoints; chosen over AutoGen for its explicit state machine model"],
        ["CrewAI",            "Role-based agent definitions",   "MIT",          "Defines each specialist (Compliance Agent, RCA Agent, Knowledge Copilot) as a named role with a goal, backstory, and tool set; crew collaboration lets agents hand off findings between roles"],
        ["LangChain",         "Tool & chain primitives",        "MIT",          "Provides the retrieval chains, prompt templates, and tool wrappers that each agent uses; deeply integrated with both Qdrant and Neo4j"],
        ["AutoGen (optional)","Code-executing RCA sub-agent",   "MIT",          "Used optionally for the RCA agent when failure analysis requires running Python calculations (e.g., MTBF, Weibull fits) rather than pure text reasoning"],
      ]),
      spacer(),

      // Layer 5
      h2("Layer 5 — Compliance intelligence engine (centrepiece)"),
      body("This is the hackathon demo focus. Four sub-components work in sequence:"),
      bullet("Regulatory Mapper: Loads OISD-118, PESO Form 17, Factories Act §41G, and BIS standards into Qdrant as typed regulation chunks with clause-level metadata. Uses OntoGPT to extract threshold values, equipment scope, and inspection frequency requirements."),
      bullet("Gap Detector: The Compliance Agent (CrewAI) retrieves current equipment state from Neo4j (last inspection date, SOP version, work order history) and compares against regulation requirements. Output is a structured gap list with severity (Critical / Major / Minor), the regulation clause violated, and the source document link."),
      bullet("Evidence Packager: Auto-generates a compliance evidence package (PDF report) per gap, citing the exact document, page, and extracted clause. Uses ReportLab (open source) to render structured audit-ready PDFs without manual effort."),
      bullet("Alert Engine: Pushes Critical gaps to a mock mobile notification endpoint (FastAPI webhook) with equipment tag, gap description, and remediation link. In production this would route to an FCM / WhatsApp Business API for field technicians."),
      spacer(),

      // Additional open-source resources
      h2("Additional open-source tools (beyond the brief)"),
      layerTable("Additional Resources", BLUE, [
        ["RAGAS",             "RAG evaluation framework",       "Apache 2.0",   "Measures faithfulness, answer relevance, and context recall for the Knowledge Copilot — critical for the hackathon's evaluation criterion on query answer quality"],
        ["Label Studio",      "Annotation for entity eval",     "Apache 2.0",   "Open-source annotation UI for building the ground-truth entity benchmark used to measure GraphRAG extraction accuracy"],
        ["ReportLab",         "Audit PDF generation",           "BSD",          "Python library for programmatic PDF creation; used by the Evidence Packager to render compliance gap reports with table-formatted findings and regulation citations"],
        ["FastAPI",           "API + webhook server",           "MIT",          "Lightweight async Python framework powering the REST API layer, the alert webhook endpoint, and the admin document upload interface"],
        ["Presidio",          "PII redaction before indexing",  "MIT",          "Microsoft's open-source PII detection + anonymisation; strips personnel names and Aadhaar numbers from documents before they enter the knowledge graph"],
        ["Docling (IBM)",     "Complex PDF parsing",            "MIT",          "IBM's new open-source PDF understanding library (Dec 2024); excels at extracting structured content from dense regulatory PDFs where PaddleOCR layout detection struggles"],
        ["Chonkie",           "Semantic chunking",              "MIT",          "Semantic-aware chunker that respects clause boundaries in regulatory text — avoids splitting a compliance requirement mid-sentence, improving RAG retrieval precision"],
      ]),
      spacer(),

      // Layer 6
      h2("Layer 6 — Interfaces"),
      bullet("Web dashboard (React + D3 force graph): compliance gap heatmap, knowledge graph explorer (Node = equipment/reg/SOP, Edge = relationship type), and RAG copilot chat panel."),
      bullet("Mobile view (responsive): field technician gap alerts with one-tap access to source documents."),
      bullet("REST API (FastAPI): QMS integration hooks, SCADA data push endpoint, and admin document upload."),
      spacer(),

      // ── 3. MOCK DATA ──────────────────────────────────────────────
      h1("3.  Mock data strategy (no real documents needed)"),
      body("Since we are generating synthetic data, each mock document is designed to create at least one compliance gap that the Compliance Agent must detect. This makes the demo self-contained and reproducible for judges."),
      spacer(),
      mockDataTable(),
      spacer(),
      body("Mock data generation script: a single Python script (generate_mock_corpus.py) will output all six files to a /data/mock directory using Faker (industrial extension) + hand-authored regulatory clause text. Each document is intentionally 'broken' in one specific way — an overdue inspection, a missing lock-out step, an incorrect pressure rating — so the gap detector has clear targets.", { italic: true }),
      spacer(),

      // ── 4. IMPLEMENTATION PLAN ───────────────────────────────────
      h1("4.  Implementation plan"),
      h2("Day 1 — Foundation (Hours 0–12)"),
      bullet("Set up monorepo: /ingest, /graph, /agents, /compliance, /api, /frontend", "numbers"),
      bullet("Implement ingestion pipeline: PaddleOCR + Surya → text chunks → Qdrant", "numbers"),
      bullet("Stand up Neo4j + run GraphRAG on mock corpus to build initial graph", "numbers"),
      bullet("Verify entity extraction: equipment tags, regulation references visible in Neo4j browser", "numbers"),
      spacer(),
      h2("Day 2 — Agent layer (Hours 12–24)"),
      bullet("Implement Compliance Agent in CrewAI: give it tools for Qdrant retrieval + Neo4j Cypher", "numbers"),
      bullet("Implement Regulatory Mapper: load OISD-118 mock clauses into Qdrant with metadata", "numbers"),
      bullet("Implement Gap Detector: agent compares equipment state graph vs. regulation requirements", "numbers"),
      bullet("Wire LangGraph orchestrator: route /query → Compliance Agent or Knowledge Copilot", "numbers"),
      spacer(),
      h2("Day 3 — Demo polish (Hours 24–36)"),
      bullet("Build Evidence Packager: ReportLab PDF with ranked gap table + source citations", "numbers"),
      bullet("Build React dashboard: gap heatmap + D3 knowledge graph + RAG chat panel", "numbers"),
      bullet("Run RAGAS eval on 20 benchmark questions; tune retrieval if score <0.70", "numbers"),
      bullet("Record demo video: live query → gap detection → audit PDF generation flow", "numbers"),
      spacer(),

      // ── 5. EVALUATION READINESS ──────────────────────────────────
      h1("5.  Evaluation readiness"),
      evalTable(),
      spacer(),

      // ── 6. RISK REGISTER ─────────────────────────────────────────
      h1("6.  Risks and mitigations"),
      bullet("LayoutLMv3 GPU requirement: if no GPU available, fall back to Surya-only layout + PaddleOCR text for P&IDs. Slightly lower entity accuracy on diagrams but pipeline stays live."),
      bullet("GraphRAG index build time: pre-build the Neo4j graph from mock corpus before the demo. Provide a pre-seeded Neo4j Docker image as a backup."),
      bullet("LLM API rate limits: all GraphRAG and agent LLM calls route through an Ollama local instance (Mistral 7B or Llama 3 8B) as fallback if Claude/GPT API quota is hit during the demo."),
      bullet("P&ID parsing accuracy: P&IDs are the hardest document type. For the demo, use two or three pre-processed P&IDs with verified entity extraction rather than live parsing unknown drawings."),
      spacer(),

      // ── 7. TECH STACK SUMMARY ────────────────────────────────────
      h1("7.  Complete tech stack at a glance"),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [1800, 2560, 3200, 1800],
        rows: [
          hrow([
            cell("Layer",    { fill: BLUE, bold: true, color: WHITE, size: 20, width: 1800 }),
            cell("Primary",  { fill: BLUE, bold: true, color: WHITE, size: 20, width: 2560 }),
            cell("Purpose",  { fill: BLUE, bold: true, color: WHITE, size: 20, width: 3200 }),
            cell("License",  { fill: BLUE, bold: true, color: WHITE, size: 20, width: 1800 }),
          ]),
          row([cell("OCR",          {fill:WHITE,   bold:false, width:1800}), cell("PaddleOCR v3 + Surya",          {fill:WHITE, width:2560}),   cell("Text, table, layout extraction from any document format", {fill:WHITE, width:3200}),   cell("Apache 2.0",   {fill:WHITE, width:1800})]),
          row([cell("Vision",       {fill:GRAY_BG, bold:false, width:1800}), cell("LayoutLMv3",                   {fill:GRAY_BG, width:2560}), cell("P&ID multimodal entity parsing (text + layout + image)",  {fill:GRAY_BG, width:3200}), cell("CC BY-NC 4.0", {fill:GRAY_BG, width:1800})]),
          row([cell("Parsing",      {fill:WHITE,   bold:false, width:1800}), cell("Unstructured.io + Docling",    {fill:WHITE, width:2560}),   cell("Email, XLSX, complex regulatory PDF parsing",             {fill:WHITE, width:3200}),   cell("Apache 2.0 / MIT", {fill:WHITE, width:1800})]),
          row([cell("Graph build",  {fill:GRAY_BG, bold:false, width:1800}), cell("Microsoft GraphRAG + OntoGPT", {fill:GRAY_BG, width:2560}), cell("Entity extraction → knowledge graph construction",        {fill:GRAY_BG, width:3200}), cell("MIT",          {fill:GRAY_BG, width:1800})]),
          row([cell("Graph DB",     {fill:WHITE,   bold:false, width:1800}), cell("Neo4j Community",              {fill:WHITE, width:2560}),   cell("Persistent property graph with Cypher query support",      {fill:WHITE, width:3200}),   cell("GPL 3.0",      {fill:WHITE, width:1800})]),
          row([cell("Vector store", {fill:GRAY_BG, bold:false, width:1800}), cell("Qdrant",                       {fill:GRAY_BG, width:2560}), cell("Dense retrieval with metadata filtering",                  {fill:GRAY_BG, width:3200}), cell("Apache 2.0",   {fill:GRAY_BG, width:1800})]),
          row([cell("Chunking",     {fill:WHITE,   bold:false, width:1800}), cell("Chonkie",                      {fill:WHITE, width:2560}),   cell("Semantic-aware clause-boundary chunking",                  {fill:WHITE, width:3200}),   cell("MIT",          {fill:WHITE, width:1800})]),
          row([cell("Orchestrator", {fill:GRAY_BG, bold:false, width:1800}), cell("LangGraph",                   {fill:GRAY_BG, width:2560}), cell("Stateful multi-agent runtime with cyclic graphs",          {fill:GRAY_BG, width:3200}), cell("MIT",          {fill:GRAY_BG, width:1800})]),
          row([cell("Agents",       {fill:WHITE,   bold:false, width:1800}), cell("CrewAI + LangChain",           {fill:WHITE, width:2560}),   cell("Role-based specialist agents; retrieval chains + tools",   {fill:WHITE, width:3200}),   cell("MIT",          {fill:WHITE, width:1800})]),
          row([cell("LLM runtime",  {fill:GRAY_BG, bold:false, width:1800}), cell("Claude API + Ollama fallback", {fill:GRAY_BG, width:2560}), cell("LLM inference for entity extraction, reasoning, Q&A",     {fill:GRAY_BG, width:3200}), cell("Commercial/MIT",{fill:GRAY_BG, width:1800})]),
          row([cell("PII safety",   {fill:WHITE,   bold:false, width:1800}), cell("Presidio",                     {fill:WHITE, width:2560}),   cell("PII detection + redaction before graph indexing",          {fill:WHITE, width:3200}),   cell("MIT",          {fill:WHITE, width:1800})]),
          row([cell("Compliance",   {fill:GRAY_BG, bold:false, width:1800}), cell("Custom compliance engine",     {fill:GRAY_BG, width:2560}), cell("Reg mapper + gap detector + evidence packager + alerts",   {fill:GRAY_BG, width:3200}), cell("Custom",       {fill:GRAY_BG, width:1800})]),
          row([cell("Audit PDF",    {fill:WHITE,   bold:false, width:1800}), cell("ReportLab",                    {fill:WHITE, width:2560}),   cell("Programmatic PDF generation for compliance evidence packs", {fill:WHITE, width:3200}),   cell("BSD",          {fill:WHITE, width:1800})]),
          row([cell("API",          {fill:GRAY_BG, bold:false, width:1800}), cell("FastAPI",                      {fill:GRAY_BG, width:2560}), cell("REST API, webhook server, admin upload interface",         {fill:GRAY_BG, width:3200}), cell("MIT",          {fill:GRAY_BG, width:1800})]),
          row([cell("Evaluation",   {fill:WHITE,   bold:false, width:1800}), cell("RAGAS + Label Studio",         {fill:WHITE, width:2560}),   cell("RAG quality scoring; entity annotation ground-truth",      {fill:WHITE, width:3200}),   cell("Apache 2.0",   {fill:WHITE, width:1800})]),
          row([cell("Frontend",     {fill:GRAY_BG, bold:false, width:1800}), cell("React + D3.js",                {fill:GRAY_BG, width:2560}), cell("Knowledge graph explorer, compliance dashboard, RAG chat",  {fill:GRAY_BG, width:3200}), cell("MIT",          {fill:GRAY_BG, width:1800})]),
        ]
      }),
      spacer(),

      // Footer note
      divider(),
      body("PlantBrain  ·  Economic Times AI Hackathon 2026  ·  Problem 8 — Industrial Knowledge Intelligence  ·  All tools open-source unless noted", { italic: true, color: "888888" }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/mnt/user-data/outputs/PlantBrain_TechStack.docx", buf);
  console.log("Done: PlantBrain_TechStack.docx");
});
