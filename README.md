# parsing_exercises

Practice project for building scientific-data parsers and transforming messy instrument outputs with `pandas`.

The goal is to simulate the kind of work a Senior Scientific Data Engineer would do when ingesting lab exports, vendor files, and semi-structured operational data into clean analytical tables.

## Why these exercises matter

These fixtures are designed to rehearse the same skills that show up in scientific data engineering work:

- parsing instrument exports from mixed formats
- flattening nested payloads into tabular models
- handling metadata, headers, and odd file conventions
- normalizing units, timestamps, flags, and identifiers
- building reusable parsing utilities
- designing tests for parser correctness and data quality

## Fixture catalog

All practice files live under `fixtures/`.

### 1. HPLC sequence export

- File: `fixtures/01_hplc/hplc_sequence_report.tsv`
- Format: tab-separated text with metadata comment lines
- Real-world behavior to mimic:
	- preamble rows before the actual header
	- blank retention times for blanks / non-integrated peaks
	- QC flags that need interpretation
	- sample dilution factors that matter during downstream normalization

#### Parser tasks

- skip metadata lines beginning with `#`
- load the tabular section into a `DataFrame`
- coerce numeric columns safely
- convert blank `rt_min` values to missing values
- separate calibration rows, QC rows, blanks, and unknown samples

#### Transformation tasks

- compute adjusted concentration after dilution handling
- flag reinjections and RT-shifted samples
- build a sample-level summary table from injection-level data
- calculate QC pass rates per run

#### Suggested tests

- assert the row count is `8`
- assert `BLANK-01` has null `rt_min`
- assert `SMP-103` is identified as a reinjection candidate
- assert only one sequence ID exists in the file

---

### 2. Plate reader workbook

- File: `fixtures/02_plate_reader/plate_reader_export.xlsx`
- Format: Excel workbook with `Metadata` and `Readings` sheets
- Real-world behavior to mimic:
	- metadata stored separately from measurement rows
	- plate/well-based assay layout
	- one failed reading marked for repeat
	- blank-corrected values included alongside raw RFU

#### Parser tasks

- read workbook-level metadata from the `Metadata` sheet
- parse the `Readings` sheet into a clean `DataFrame`
- standardize column names to snake_case
- interpret the repeated-read record in well `C01`

#### Transformation tasks

- calculate signal fold-change versus blank or vehicle wells
- group by `condition` and summarize RFU distributions
- generate a long-form assay result table keyed by `plate_id`, `well`, and `sample_id`
- attach workbook metadata to each reading row

#### Suggested tests

- assert both sheets are present
- assert `plate_id == "PLATE-8821"`
- assert one row is flagged `REPEAT_READ`
- assert the parser preserves `well` identities exactly

---

### 3. LC-MS peak report

- File: `fixtures/03_mass_spec/lcms_peak_report.txt`
- Format: structured plain text report with multiple sections
- Real-world behavior to mimic:
	- report headers mixed with tables
	- repeated peak-table sections per unknown sample
	- separate system-suitability section
	- failed acquisitions appearing in summary rows

#### Parser tasks

- extract batch-level metadata from the header
- parse the `[Sample Summary]` block
- detect each `[Peak Table: ...]` section and parse it into rows
- parse the `[System Suitability]` section into a separate table

#### Transformation tasks

- combine all peak tables into one normalized result set
- calculate `mz_error_ppm`
- flag low-confidence peaks using `score` and `S/N`
- join peak data back to the sample summary on sample/file identity

#### Suggested tests

- assert there are `2` parsed peak tables
- assert `UNK_203` is marked failed in the summary
- assert `Impurity_A` in `UNK_202` is flagged as suspicious
- assert all system-suitability metrics are parsed into key/value rows

---

### 4. Instrument audit stream

- File: `fixtures/04_audit_jsonl/instrument_events.jsonl`
- Format: JSON Lines with nested payloads
- Real-world behavior to mimic:
	- heterogeneous event payloads
	- nested arrays and nullable fields
	- event-style observability data rather than tidy rows

#### Parser tasks

- read the file as JSON Lines
- flatten the nested `payload` object
- preserve `tags` in a normalized way
- handle different schemas by `event_type`

#### Transformation tasks

- produce a unified event table with common columns
- create event-type-specific subtables for readings, alarms, and maintenance
- calculate freezer recovery time after the alarm event
- build a timeline of door-open and temperature excursions

#### Suggested tests

- assert there are `5` events
- assert exactly one `alarm` event exists
- assert the maintenance event expands its `actions` field correctly
- assert null acknowledgements are preserved as missing values

---

### 5. Environment monitor XML

- File: `fixtures/05_environment_xml/freezer_monitor_log.xml`
- Format: XML with namespaces, attributes, and nested elements
- Real-world behavior to mimic:
	- namespaced XML exports
	- readings represented as attributes
	- alarms represented as nested elements with text nodes

#### Parser tasks

- parse XML with namespace handling
- extract instrument metadata and location fields
- turn `<env:reading />` nodes into a tabular structure
- turn alarm nodes into a separate alarm table

#### Transformation tasks

- compute max temperature excursion during the incident window
- join alarm windows to nearby readings
- normalize boolean attribute values like `doorOpen`
- produce a clean star-schema-style output: instrument, readings, alarms

#### Suggested tests

- assert four reading rows are parsed
- assert one alarm row is parsed
- assert the site value is `BOS`
- assert the namespace does not block extraction

---

### 6. Certificate-of-analysis PDF

- File: `fixtures/06_pdf_report/coa_report.pdf`
- Format: simple PDF text report
- Real-world behavior to mimic:
	- data embedded in report-like text instead of a clean table
	- extraction usually requires a PDF text layer tool before parsing

#### Parser tasks

- extract text from the PDF
- identify key-value pairs such as batch, sample, analyte, result, and specification
- normalize the extracted fields into a row-oriented table

#### Transformation tasks

- compare numeric result vs. specification bounds
- derive an `in_spec` boolean
- create a standard COA schema compatible with other assay result tables

#### Suggested tests

- assert the PDF text contains the expected sample ID context
- assert the numeric result parses as `98.4`
- assert the spec range parses into low/high bounds

---

### 7. Vendor-style NMR / raw assets

- Files:
	- `fixtures/07_nmr_vendor/acqus`
	- `fixtures/07_nmr_vendor/fid`
	- `fixtures/07_nmr_vendor/sample_run.raw`
- Format: parameter text + binary-like payloads
- Real-world behavior to mimic:
	- instrument runs often arrive as multi-file bundles
	- metadata is sometimes in text sidecars while signal data is binary
	- parsers often start with header decoding before signal interpretation

#### Parser tasks

- parse `acqus` as a key/value parameter file
- infer acquisition settings such as nucleus, frequency, spectral width, and scan count
- inspect the binary files and document an assumed byte layout
- prototype a minimal binary reader for the fake `fid` file

#### Transformation tasks

- produce a run manifest that combines parsed text metadata with binary file stats
- decode the fake `fid` signal into signed integer pairs
- extract null-delimited fields from `sample_run.raw`

#### Suggested tests

- assert required `acqus` keys exist
- assert `fid` byte length matches the expected mock payload length
- assert the raw file starts with the expected magic header

## Recommended implementation plan

If you want to practice this like a real project, implement in this order:

1. build one parser module per fixture
2. return standardized `DataFrame` outputs
3. add validation utilities for required columns, types, and null rules
4. add unit tests for parsing
5. add transformation tests for downstream analytics logic
6. optionally add a small CLI that parses every fixture into `outputs/`

## Suggested package structure

One reasonable structure:

```text
parsers/
	hplc.py
	plate_reader.py
	lcms.py
	audit_jsonl.py
	freezer_xml.py
	coa_pdf.py
	vendor_nmr.py
tests/
	test_hplc.py
	test_plate_reader.py
	test_lcms.py
	test_audit_jsonl.py
	test_freezer_xml.py
	test_coa_pdf.py
	test_vendor_nmr.py
```

## Senior-level practice goals

To align these exercises with the target role, try to practice beyond just “reading files”:

- define canonical schemas for each parser output
- separate raw parsing from business-rule transformations
- write reusable utilities for units, timestamps, and identifier cleanup
- log warnings for suspicious data instead of silently dropping rows
- design tests for both happy-path and malformed-input behavior
- think about how each parser could scale into a production ingestion service

## Stretch tasks

- add malformed variants of each fixture and test failure handling
- create a batch orchestrator that parses all fixture folders
- add a data-quality report for every run
- persist normalized outputs as parquet
- write SQL models on top of the normalized outputs
