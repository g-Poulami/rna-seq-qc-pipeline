#!/usr/bin/env python3
"""
count_kmers.py
--------------
Count the frequency of every k-mer (sub-string of length k) found
across all reads in a FASTQ file.

Output: tab-separated file  <kmer> <count>  sorted by descending count.
"""

import argparse
import os
import sys
from collections import Counter


VALID_BASES = set("ACGT")


def iter_sequences(fastq_path: str):
    """Yield just the sequence line from each FASTQ record."""
    with open(fastq_path) as fh:
        line_num = 0
        for line in fh:
            line_num += 1
            if line_num % 4 == 2:       # every 2nd line in a 4-line record
                yield line.rstrip()


def count_kmers(fastq_path: str, k: int) -> Counter:
    counts: Counter = Counter()
    for seq in iter_sequences(fastq_path):
        # skip k-mers that contain ambiguous or error bases
        for i in range(len(seq) - k + 1):
            kmer = seq[i : i + k]
            if all(b in VALID_BASES for b in kmer):
                counts[kmer] += 1
    return counts


def write_tsv(counts: Counter, output_path: str):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as fh:
        fh.write("kmer\tcount\n")
        for kmer, cnt in counts.most_common():
            fh.write(f"{kmer}\t{cnt}\n")


def main():
    parser = argparse.ArgumentParser(description="Count k-mer frequencies in FASTQ")
    parser.add_argument("--input",  required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--k",      type=int, default=4)
    args = parser.parse_args()

    print(f"Counting {args.k}-mers in {args.input} …", file=sys.stderr)
    counts = count_kmers(args.input, args.k)

    write_tsv(counts, args.output)

    total_kmers  = sum(counts.values())
    unique_kmers = len(counts)
    print(
        f"Found {unique_kmers} unique {args.k}-mers "
        f"({total_kmers:,} total occurrences) → {args.output}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
