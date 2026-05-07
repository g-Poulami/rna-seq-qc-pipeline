# RNA-seq-QC-Pipeline

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Containerised-blue?style=flat-square&logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)]()

A **containerised, reproducible** RNA-seq quality control pipeline implementing a four-step DAG for assessing sequencing quality, detecting artefacts, and generating a consolidated report before downstream alignment and quantification.

---

## Overview

Quality control is the essential first step in any RNA-seq project. Poor-quality samples, adapter contamination, or rRNA carryover that escape detection at this stage propagate errors into all downstream analyses. This pipeline provides a standardised, automated QC workflow that is fully containerised — guaranteeing identical results regardless of host environment — and produces both per-sample and aggregated reports for easy interpretation.

---

## Four-Step DAG

```
Step 1: FastQC
  Raw paired FASTQs --> per-read quality metrics, adapter content,
                        duplication rates, GC distribution

        |
        v

Step 2: Trimmomatic
  FastQC reports --> adapter removal, leading/trailing quality trimming,
                     sliding window filtering, minimum length filtering

        |
        v

Step 3: FastQC (post-trim)
  Trimmed FASTQs --> confirm adapter removal, verify quality improvement

        |
        v

Step 4: MultiQC
  All FastQC reports --> consolidated HTML report across all samples
```

---

## Key Features

- **Fully containerised**: Docker image bundles FastQC, Trimmomatic, and MultiQC — no local installation required
- **Four-step DAG**: each step depends strictly on the previous, enforcing correct execution order
- **Multi-sample ready**: processes all `*_R{1,2}.fastq.gz` files in the input directory in parallel
- **Consolidated reporting**: MultiQC aggregates per-sample FastQC metrics into a single interactive HTML report
- **Reproducible**: pinned software versions in the Docker image guarantee consistent results

---

## Requirements

Docker must be installed. No other local dependencies are required.

```bash
docker --version  # Docker 20.10+
```

---

## Quick Start

### Pull and run

```bash
git clone https://github.com/g-Poulami/RNA-seq-QC-Pipeline.git
cd RNA-seq-QC-Pipeline

# Build Docker image
docker build -t rnaseq-qc .

# Run on your data
docker run --rm \
  -v /path/to/fastq:/data/raw \
  -v /path/to/results:/results \
  rnaseq-qc \
  --input /data/raw \
  --output /results
```

### Run with Docker Compose

```bash
# Edit paths in docker-compose.yml, then:
docker-compose up
```

---

## Configuration

Edit `config.yaml` to customise trimming parameters:

```yaml
input_dir: data/raw/
output_dir: results/

trimmomatic:
  adapters: assets/TruSeq3-PE.fa
  leading: 3
  trailing: 3
  sliding_window: "4:15"
  min_len: 36
  threads: 4

multiqc:
  title: "RNA-seq QC Report"
  filename: multiqc_report.html
```

---

## Outputs

| File/Directory | Description |
|----------------|-------------|
| `results/fastqc_raw/` | Per-sample FastQC HTML + ZIP (raw reads) |
| `results/trimmed/` | Quality-trimmed FASTQ files |
| `results/fastqc_trimmed/` | Per-sample FastQC HTML + ZIP (trimmed reads) |
| `results/multiqc/multiqc_report.html` | Aggregated interactive QC report |
| `results/multiqc/multiqc_data/` | Raw data tables underlying the MultiQC report |

---

## Interpreting the MultiQC Report

Key metrics to review in the consolidated report:

| Metric | Acceptable Range | Action if Failed |
|--------|-----------------|------------------|
| Per-base sequence quality | Q > 28 across read | Increase trimming stringency |
| Adapter content | < 1% post-trim | Check adapter file matches library prep |
| % Duplicates | < 60% for total RNA | Expected higher for poly-A enriched |
| GC content | Species-appropriate | Investigate rRNA or contamination |
| Sequence length distribution | Consistent across samples | Flag outlier samples |

---

## Docker Image Contents

| Tool | Version | Purpose |
|------|---------|---------|
| FastQC | 0.12.1 | Per-read quality assessment |
| Trimmomatic | 0.39 | Adapter and quality trimming |
| MultiQC | 1.17 | Report aggregation |
| Python | 3.10 | Pipeline orchestration |

---

## Project Structure

```
RNA-seq-QC-Pipeline/
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Compose configuration
├── run_qc.py                  # Pipeline orchestrator
├── config.yaml                # User parameters
├── assets/
│   ├── TruSeq3-PE.fa          # Illumina adapter sequences
│   └── NexteraPE-PE.fa        # Nextera adapter sequences
├── data/
│   └── raw/                   # Input FASTQs (not tracked)
└── results/                   # Pipeline outputs
```

---

## Notes

This pipeline produces QC-filtered reads ready for alignment. Typical next steps are splice-aware alignment (STAR or HISAT2) followed by quantification (featureCounts or Salmon), which are implemented in the companion [Nextflow-RNA-seq-Pipeline](https://github.com/g-Poulami/Nextflow-RNA-seq-Pipeline) repository.

---

## License

MIT

---

## Author

Poulami Ghosh — [LinkedIn](https://linkedin.com/in/poulami-ghosh-879439304) | [Google Scholar](https://scholar.google.com)
