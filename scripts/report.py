#!/usr/bin/env python3
"""
report.py
---------
Aggregate per-sample filter statistics and k-mer counts into a
human-readable plain-text summary report.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


SEPARATOR = "─" * 70


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


def load_kmer_table(path):
    rows = []
    with open(path) as fh:
        next(fh)  # skip header
        for line in fh:
            parts = line.rstrip().split("\t")
            if len(parts) == 2:
                rows.append((parts[0], int(parts[1])))
    return rows


def format_report(samples, stats_dir):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        SEPARATOR,
        "  RNA-seq QC Pipeline — Summary Report",
        f"  Generated: {now}",
        SEPARATOR,
        "",
    ]

    # Per-sample QC table
    lines.append("  QUALITY FILTERING RESULTS")
    lines.append("")
    header = f"  {'Sample':<15} {'Total':>8} {'Kept':>8} {'Disc.Q':>8} {'Disc.L':>8} {'Pass%':>7}"
    lines.append(header)
    lines.append("  " + "-" * 58)

    totals = {"total": 0, "kept": 0, "discarded_qual": 0, "discarded_len": 0}
    for sample in samples:
        stats_path = os.path.join(stats_dir, sample, "filter_stats.json")
        s = load_json(stats_path)
        for k in totals:
            totals[k] += s[k]
        pct = s["pass_rate"] * 100
        lines.append(
            f"  {sample:<15} {s['total']:>8,} {s['kept']:>8,} "
            f"{s['discarded_qual']:>8,} {s['discarded_len']:>8,} {pct:>6.1f}%"
        )

    lines.append("  " + "-" * 58)
    total_pct = totals["kept"] / totals["total"] * 100 if totals["total"] else 0
    lines.append(
        f"  {'TOTAL':<15} {totals['total']:>8,} {totals['kept']:>8,} "
        f"{totals['discarded_qual']:>8,} {totals['discarded_len']:>8,} {total_pct:>6.1f}%"
    )
    lines.append("")

    # Top k-mers per sample
    lines.append("  TOP 10 K-MERS PER SAMPLE")
    lines.append("")

    for sample in samples:
        kmer_path = os.path.join(stats_dir, sample, "kmers.tsv")
        kmers = load_kmer_table(kmer_path)
        total_occ = sum(c for _, c in kmers)
        lines.append(f"  [{sample}]  ({len(kmers)} unique k-mers, {total_occ:,} total occurrences)")
        lines.append(f"  {'Rank':<6} {'K-mer':<12} {'Count':>8} {'Freq%':>8}")
        lines.append("  " + "-" * 38)
        for rank, (kmer, cnt) in enumerate(kmers[:10], start=1):
            freq = cnt / total_occ * 100 if total_occ else 0
            lines.append(f"  {rank:<6} {kmer:<12} {cnt:>8,} {freq:>7.2f}%")
        lines.append("")

    lines.append(SEPARATOR)
    lines.append("  Pipeline completed successfully.")
    lines.append(SEPARATOR)
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate pipeline summary report")
    parser.add_argument("--samples",   nargs="+", required=True)
    parser.add_argument("--stats-dir", default="results")
    parser.add_argument("--output",    required=True)
    args = parser.parse_args()

    report = format_report(args.samples, args.stats_dir)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as fh:
        fh.write(report)

    print(report, file=sys.stderr)
    print(f"Report written -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
