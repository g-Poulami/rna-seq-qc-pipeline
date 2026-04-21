#!/usr/bin/env python3
"""
filter_reads.py
---------------
Remove reads that fall below a minimum mean Phred quality score
or are shorter than a minimum length.

Writes:
  - filtered FASTQ  (reads that pass)
  - JSON stats file (counts kept / discarded)
"""

import argparse
import json
import os
import sys


def phred_score(char: str) -> int:
    """Convert a single Sanger-encoded quality character to a Phred integer."""
    return ord(char) - 33


def mean_quality(qual_str: str) -> float:
    return sum(phred_score(c) for c in qual_str) / len(qual_str)


def parse_fastq(path: str):
    """Yield (header, seq, qual) tuples from a FASTQ file."""
    with open(path) as fh:
        while True:
            header = fh.readline().rstrip()
            if not header:
                break
            seq    = fh.readline().rstrip()
            _plus  = fh.readline()
            qual   = fh.readline().rstrip()
            yield header, seq, qual


def filter_reads(input_path, output_path, stats_path, min_qual, min_len):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    kept = discarded_qual = discarded_len = 0

    with open(output_path, "w") as out:
        for header, seq, qual in parse_fastq(input_path):
            if len(seq) < min_len:
                discarded_len += 1
                continue
            if mean_quality(qual) < min_qual:
                discarded_qual += 1
                continue
            out.write(f"{header}\n{seq}\n+\n{qual}\n")
            kept += 1

    total = kept + discarded_qual + discarded_len
    stats = {
        "total":          total,
        "kept":           kept,
        "discarded_qual": discarded_qual,
        "discarded_len":  discarded_len,
        "pass_rate":      round(kept / total, 4) if total else 0,
    }

    with open(stats_path, "w") as sf:
        json.dump(stats, sf, indent=2)

    print(
        f"Filter complete: {kept}/{total} reads kept "
        f"({stats['pass_rate']*100:.1f} %) → {output_path}",
        file=sys.stderr,
    )
    return stats


def main():
    parser = argparse.ArgumentParser(description="Filter low-quality FASTQ reads")
    parser.add_argument("--input",    required=True)
    parser.add_argument("--output",   required=True)
    parser.add_argument("--stats",    required=True)
    parser.add_argument("--min-qual", type=float, default=20.0)
    parser.add_argument("--min-len",  type=int,   default=50)
    args = parser.parse_args()

    filter_reads(args.input, args.output, args.stats, args.min_qual, args.min_len)


if __name__ == "__main__":
    main()
