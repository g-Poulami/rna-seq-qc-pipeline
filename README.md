[![CI](https://github.com/g-Poulami/rna-seq-qc-pipeline/actions/workflows/ci.yml/badge.svg)](...)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue?style=flat-square)](LICENSE)
# RNA-seq QC Pipeline [*Live QC Dashboard*](https://g-Poulami.github.io/rna-seq-qc-pipeline/pipeline_qc_dashboard.html)
A minimal but realistic bioinformatics pipeline built with **Snakemake** and
containerised with **Docker**.

```
generate_reads  →  filter_reads  →  count_kmers  →  report
      ↑                  ↑               ↑              ↑
 (per sample)       (per sample)    (per sample)   (all samples)
```

## Pipeline steps

| Rule | Script | Input | Output |
| --- | --- | --- | --- |
| `generate_reads` | `generate_reads.py` | — | `data/{sample}/reads.fastq` |
| `filter_reads` | `filter_reads.py` | FASTQ | `results/{sample}/filtered.fastq` + stats JSON |
| `count_kmers` | `count_kmers.py` | filtered FASTQ | `results/{sample}/kmers.tsv` |
| `report` | `report.py` | all stats + k-mer TSVs | `results/report.txt` |

## Project layout

```
pipeline/
├── Dockerfile
├── Snakefile          # DAG definition
├── config.yaml        # samples, thresholds, k-mer k
├── scripts/
│   ├── generate_reads.py
│   ├── filter_reads.py
│   ├── count_kmers.py
│   └── report.py
├── data/              # generated at runtime
├── results/           # outputs land here
└── logs/              # per-rule stderr logs
```

## QC dashboard insights

The [live dashboard](https://g-Poulami.github.io/rna-seq-qc-pipeline/pipeline_qc_dashboard.html) summarises results across **3 samples × 1,000 reads** simulated with the default config (`error_rate=0.02`, `read_len=100`, `kmer_k=4`).

### Quality scores

All 3,000 reads pass the Q20 threshold, confirming that the simulated error rate and the `min_quality=20` filter are well-matched. Per-read mean Phred scores fall in a tight band of roughly **32.3–35.8** across all samples, with per-sample means converging to **~34.2**. The distributions are unimodal and right-skewed, peaking around Q34.0–34.25, which is consistent with a 2% uniform error rate.

| Sample | Mean Phred | Min | Max | Reads passing Q20 |
| --- | --- | --- | --- | --- |
| sample_A | 34.16 | 32.25 | 35.75 | 1000 / 1000 (100%) |
| sample_B | 34.16 | 32.50 | 35.25 | 1000 / 1000 (100%) |
| sample_C | 34.17 | 32.50 | 35.50 | 1000 / 1000 (100%) |

### GC content

GC content distributions are nearly identical across samples, centred on **~50%** (median 50%, mean ~49.3–49.5%). This is the expected result for uniformly random base generation. Reads span roughly **28–64% GC**, with the bulk of reads falling between 44–54%. No sample shows GC bias or bimodality that would indicate adapter contamination or composition skew.

| Sample | Mean GC | Median GC | Range |
| --- | --- | --- | --- |
| sample_A | 49.3% | ~50% | 28–64% |
| sample_B | 49.3% | ~50% | 34–64% |
| sample_C | 49.5% | ~50% | 34–62% |

### 4-mer frequencies

All 256 possible 4-mers are observed in every sample, with counts distributed evenly between approximately **326–438** occurrences and a consistent mean of **~379** per k-mer per sample. This near-uniform coverage across the full 4-mer space confirms that the read simulator produces unbiased sequence composition. Homopolymers (AAAA, TTTT, CCCC, GGGG) are not enriched and fall within normal range alongside all other k-mers.

Top 5 most frequent 4-mers per sample (counts out of ~379 mean):

| Rank | sample_A | sample_B | sample_C |
| --- | --- | --- | --- |
| 1 | ATAG (438) | TACG (430) | TGTT (433) |
| 2 | GTGG (436) | GCTA (429) | CGTC (430) |
| 3 | CATA (435) | TGCT (426) | CGTG (425) |
| 4 | TATG (429) | CTAC (422) | AAGT (421) |
| 5 | CGTG (423) | TTCA (422) | TTTC (420) |

The top k-mers differ between samples (no shared motif dominates), and the spread from minimum to maximum count is narrow (~100 counts across 256 k-mers), reinforcing that no systematic sequence bias is introduced.

### Overall assessment

The default pipeline configuration produces high-quality, unbiased simulated reads. Every read passes quality filtering, GC content is balanced, and k-mer diversity is uniform. These results make a reliable baseline for testing downstream rule changes — any deviation from these patterns when extending the pipeline (e.g. adding a trimmer, changing the error model, or switching to real data) will be immediately visible in the dashboard.

## Running locally

```bash
# Install Snakemake
pip install snakemake
# Dry-run (shows what would execute)
snakemake --dry-run --cores 4
# Full run
snakemake --cores 4 --printshellcmds
```

## Running with Docker

```bash
# 1. Build the image
docker build -t pipeline-demo .
# 2. Run (mount results/ so outputs are accessible on the host)
docker run --rm \
  -v "$(pwd)/results:/pipeline/results" \
  pipeline-demo
# 3. Inspect the report
cat results/report.txt
```

### Override config at runtime

```bash
docker run --rm \
  -v "$(pwd)/results:/pipeline/results" \
  pipeline-demo \
  snakemake --cores all --config n_reads=5000 kmer_k=6
```

### Interactive debugging

```bash
docker run --rm -it --entrypoint bash pipeline-demo
```

## Configuration (`config.yaml`)

| Key | Default | Description |
| --- | --- | --- |
| `samples` | `[sample_A, sample_B, sample_C]` | List of sample IDs |
| `n_reads` | `1000` | Reads to simulate per sample |
| `read_len` | `100` | Read length (bp) |
| `error_rate` | `0.02` | Sequencing error probability |
| `min_quality` | `20` | Minimum mean Phred score to keep a read |
| `min_length` | `50` | Minimum read length to keep |
| `kmer_k` | `4` | k-mer length |

## Extending the pipeline

- **Real data**: skip `generate_reads` and drop real FASTQs into `data/{sample}/reads.fastq`
- **Adapter trimming**: insert a `trim_reads` rule between `generate_reads` and `filter_reads`
- **Alignment**: add a `bwa mem` or `STAR` rule after filtering
- **Cloud execution**: Snakemake supports AWS, GCP, and SLURM executors with minimal changes
