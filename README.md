# RNA-seq QC Pipeline

A minimal but realistic bioinformatics pipeline built with **Snakemake** and
containerised with **Docker**.

```
generate_reads  →  filter_reads  →  count_kmers  →  report
      ↑                  ↑               ↑              ↑
 (per sample)       (per sample)    (per sample)   (all samples)
```

## Pipeline steps

| Rule | Script | Input | Output |
|------|--------|-------|--------|
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
|-----|---------|-------------|
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
- **Cloud execution**: Snakemake supports AWS, GCP, and Slurm executors with minimal changes
