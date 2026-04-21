# ─────────────────────────────────────────────────────────────────────────────
#  RNA-seq QC Pipeline — Docker Image
#  Base: slim Python 3.12; no heavy bioinformatics deps needed.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim

LABEL maintainer="your@email.com"
LABEL description="Snakemake RNA-seq QC pipeline (generate -> filter -> kmer -> report)"

# ── System packages ───────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        procps \
    && rm -rf /var/lib/apt/lists/*

# ── Python packages ───────────────────────────────────────────────────────────
RUN pip install --no-cache-dir \
        "snakemake==8.20.3"

# ── Copy pipeline source ──────────────────────────────────────────────────────
WORKDIR /pipeline

COPY Snakefile   ./Snakefile
COPY config.yaml ./config.yaml
COPY scripts/    ./scripts/

RUN chmod +x scripts/*.py

# ── Runtime directories (override by mounting volumes) ────────────────────────
RUN mkdir -p data results logs

# ── Entrypoint ────────────────────────────────────────────────────────────────
# Mount your results dir:  docker run -v $(pwd)/results:/pipeline/results ...
CMD ["snakemake", "--cores", "all", "--printshellcmds"]
