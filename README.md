# Nextflow-RNA-seq-Pipeline

[![Nextflow](https://img.shields.io/badge/Nextflow-%E2%89%A523.04-brightgreen?style=flat-square)](https://nextflow.io)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
[![CI](https://github.com/g-Poulami/Nextflow-RNA-seq-Pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/g-Poulami/Nextflow-RNA-seq-Pipeline/actions/workflows/ci.yml)

A high-throughput, reproducible **RNA-seq processing pipeline** built in **Nextflow DSL2**, covering adapter trimming, splice-aware alignment, transcript quantification, and QC reporting for bulk transcriptomic analysis.

---

## Overview

RNA sequencing quantifies gene expression across conditions, time points, or treatment groups. This pipeline takes paired-end raw reads through all pre-processing steps required before differential expression analysis — producing per-gene count matrices, alignment statistics, and a unified QC report. The DSL2 architecture makes it straightforward to swap aligners or quantifiers without rewriting the full workflow.

---

## Pipeline Steps

```
Paired FASTQ reads
        |
        v
  FastQC (raw)              -- read quality, adapter content, duplication
        |
        v
  Trimmomatic               -- adapter removal, quality trimming
        |
        v
  FastQC (trimmed)          -- confirm trimming efficacy
        |
        v
  STAR index (once)
        |
  STAR alignment            -- splice-aware alignment to reference genome
        |
        v
  SAMtools sort & index      -- coordinate-sorted BAM
  SAMtools flagstat          -- alignment rate, pair statistics
        |
        v
  featureCounts              -- gene-level read counting
        |
        v
  MultiQC                   -- aggregated HTML report
```

---

## Key Features

- **Splice-aware alignment with STAR**: handles exon-spanning reads correctly, essential for eukaryotic transcriptomics
- **featureCounts quantification**: fast, memory-efficient gene-level counting with support for stranded library protocols
- **DSL2 module reuse**: `FASTQC` imported at two points in the pipeline (raw and trimmed) without code duplication
- **Multi-sample parallelism**: all samples processed concurrently via Nextflow's channel model
- **Profile support**: local, Docker, Singularity, conda, and SLURM execution without changing the pipeline code
- **GitHub Actions CI**: automated syntax and stub-run validation on every push

---

## Quick Start

### Install Nextflow

```bash
curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/
```

### Stub run (no tools required)

```bash
git clone https://github.com/g-Poulami/Nextflow-RNA-seq-Pipeline.git
cd Nextflow-RNA-seq-Pipeline
python3 test/generate_test_data.py
nextflow run main.nf -profile test -stub-run
```

### Run with Docker

```bash
nextflow run main.nf \
  -profile docker \
  --reads     'data/*_R{1,2}.fastq.gz' \
  --genome    'ref/genome.fa' \
  --gtf       'ref/annotation.gtf' \
  --outdir    results
```

### Resume after failure

```bash
nextflow run main.nf -resume [other params]
```

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--reads` | required | Glob pattern for paired FASTQ files |
| `--genome` | required | Reference genome FASTA |
| `--gtf` | required | Gene annotation GTF file |
| `--adapters` | `assets/adapters.fa` | Adapter sequences for Trimmomatic |
| `--strandedness` | `0` | featureCounts strandedness: 0=unstranded, 1=forward, 2=reverse |
| `--star_extra_args` | `""` | Additional STAR alignment flags |
| `--outdir` | `results` | Output directory |
| `--run_multiqc` | `true` | Aggregate QC reports |

---

## Outputs

| Directory | Contents |
|-----------|----------|
| `results/fastqc/` | FastQC HTML and ZIP (raw and trimmed) |
| `results/trimmomatic/` | Trimmed FASTQs and log files |
| `results/star/` | Aligned BAMs, splice junction tables, STAR logs |
| `results/samtools/` | Sorted BAMs, BAI indices, flagstat |
| `results/counts/` | `counts.txt` — gene × sample count matrix |
| `results/multiqc/` | `multiqc_report.html` |
| `results/pipeline_info/` | Timeline, resource report, execution DAG |

---

## Downstream Analysis

The `counts.txt` output is directly compatible with R packages for differential expression analysis:

```r
# DESeq2
library(DESeq2)
counts <- read.table("results/counts/counts.txt", skip=1, row.names=1, header=TRUE)

# edgeR
library(edgeR)
dge <- DGEList(counts = counts)
```

---

## Profiles

| Profile | Description |
|---------|-------------|
| `local` | Run locally, tools must be in PATH |
| `docker` | Pull containers from quay.io/biocontainers |
| `singularity` | Singularity images (recommended for HPC) |
| `conda` | Per-process conda environments |
| `slurm` | Submit to SLURM cluster |
| `test` | Bundled synthetic data for CI |

---

## Project Structure

```
Nextflow-RNA-seq-Pipeline/
├── main.nf
├── nextflow.config
├── assets/
│   └── adapters.fa
├── modules/
│   ├── fastqc.nf
│   ├── trimmomatic.nf
│   ├── star.nf
│   ├── samtools.nf
│   ├── featurecounts.nf
│   └── multiqc.nf
├── test/
│   ├── generate_test_data.py
│   └── data/
└── .github/
    └── workflows/
        └── ci.yml
```

---

## Reference Files (GRCh38)

| File | Source |
|------|--------|
| `hg38.fa` | UCSC Genome Browser |
| `gencode.v44.annotation.gtf` | GENCODE |
| STAR index | Generated from `hg38.fa` + GTF via `STAR_INDEX` process |

---

## License

MIT

---

## Author

Poulami Ghosh — [LinkedIn](https://linkedin.com/in/poulami-ghosh-879439304) | [Google Scholar](https://scholar.google.com)
