"""
RNA-seq QC Pipeline
===================
Steps:
  1. generate  – Simulate synthetic FASTQ reads
  2. filter    – Remove low-quality reads
  3. kmer      – Count k-mer frequencies
  4. report    – Aggregate results into a summary report

Run locally:   snakemake --cores 4
Run in Docker: docker run --rm -v $(pwd)/results:/pipeline/results pipeline-demo
"""

configfile: "config.yaml"

SAMPLES = config["samples"]
KMER_K  = config["kmer_k"]

# ── Final targets ─────────────────────────────────────────────────────────────
rule all:
    input:
        "results/report.txt",
        expand("results/{sample}/kmers.tsv", sample=SAMPLES)


# ── 1. Generate synthetic FASTQ reads ─────────────────────────────────────────
rule generate_reads:
    output:
        "data/{sample}/reads.fastq"
    params:
        n_reads    = config["n_reads"],
        read_len   = config["read_len"],
        error_rate = config["error_rate"],
        seed       = lambda wc: SAMPLES.index(wc.sample)
    log:
        "logs/{sample}/generate.log"
    shell:
        """
        python scripts/generate_reads.py \
            --output     {output} \
            --n-reads    {params.n_reads} \
            --read-len   {params.read_len} \
            --error-rate {params.error_rate} \
            --seed       {params.seed} \
            2> {log}
        """


# ── 2. Filter low-quality reads ───────────────────────────────────────────────
rule filter_reads:
    input:
        "data/{sample}/reads.fastq"
    output:
        reads   = "results/{sample}/filtered.fastq",
        stats   = "results/{sample}/filter_stats.json"
    params:
        min_qual   = config["min_quality"],
        min_length = config["min_length"]
    log:
        "logs/{sample}/filter.log"
    shell:
        """
        python scripts/filter_reads.py \
            --input    {input} \
            --output   {output.reads} \
            --stats    {output.stats} \
            --min-qual {params.min_qual} \
            --min-len  {params.min_length} \
            2> {log}
        """


# ── 3. Count k-mer frequencies ────────────────────────────────────────────────
rule count_kmers:
    input:
        "results/{sample}/filtered.fastq"
    output:
        "results/{sample}/kmers.tsv"
    params:
        k = KMER_K
    log:
        "logs/{sample}/kmer.log"
    shell:
        """
        python scripts/count_kmers.py \
            --input  {input} \
            --output {output} \
            --k      {params.k} \
            2> {log}
        """


# ── 4. Aggregate summary report ───────────────────────────────────────────────
rule report:
    input:
        stats = expand("results/{sample}/filter_stats.json", sample=SAMPLES),
        kmers = expand("results/{sample}/kmers.tsv",         sample=SAMPLES)
    output:
        "results/report.txt"
    params:
        samples = SAMPLES
    log:
        "logs/report.log"
    shell:
        """
        python scripts/report.py \
            --samples   {params.samples} \
            --stats-dir results \
            --output    {output} \
            2> {log}
        """
