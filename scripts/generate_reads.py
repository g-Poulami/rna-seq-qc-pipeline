#!/usr/bin/env python3
"""
generate_reads.py
-----------------
Simulate synthetic FASTQ reads with realistic Phred quality scores
and a configurable sequencing error rate.

Output format (4 lines per read):
  @<read_id>
  <sequence>
  +
  <quality string>
"""

import argparse
import os
import random
import string
import sys

BASES    = "ACGT"
COMP     = str.maketrans("ACGT", "TGCA")


def phred_char(q: int) -> str:
    """Convert integer Phred score to ASCII character (Sanger encoding)."""
    return chr(min(q + 33, 126))


def simulate_quality(length: int, mean_q: int = 35, std_q: int = 5, rng=None) -> list[int]:
    """Return a list of Phred scores sampled from a truncated normal distribution."""
    rng = rng or random
    scores = []
    for _ in range(length):
        q = int(rng.gauss(mean_q, std_q))
        scores.append(max(2, min(40, q)))   # clamp to [2, 40]
    return scores


def introduce_errors(seq: str, qual: list[int], error_rate: float, rng=None) -> str:
    """Replace bases probabilistically, weighting by low quality positions."""
    rng = rng or random
    bases = list(seq)
    for i, (b, q) in enumerate(zip(bases, qual)):
        p = error_rate * (1 + (40 - q) / 20)   # higher error at low quality
        if rng.random() < p:
            bases[i] = rng.choice([x for x in BASES if x != b])
    return "".join(bases)


def random_sequence(length: int, rng=None) -> str:
    rng = rng or random
    return "".join(rng.choices(BASES, k=length))


def generate_fastq(n_reads: int, read_len: int, error_rate: float, seed: int):
    rng = random.Random(seed)
    reads = []
    for i in range(n_reads):
        seq  = random_sequence(read_len, rng)
        qual = simulate_quality(read_len, rng=rng)
        seq  = introduce_errors(seq, qual, error_rate, rng)
        qual_str = "".join(phred_char(q) for q in qual)
        reads.append((f"read_{i+1}", seq, qual_str))
    return reads


def main():
    parser = argparse.ArgumentParser(description="Simulate synthetic FASTQ reads")
    parser.add_argument("--output",      required=True,  help="Output FASTQ file")
    parser.add_argument("--n-reads",     type=int,   default=1000)
    parser.add_argument("--read-len",    type=int,   default=100)
    parser.add_argument("--error-rate",  type=float, default=0.02)
    parser.add_argument("--seed",        type=int,   default=42)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    reads = generate_fastq(args.n_reads, args.read_len, args.error_rate, args.seed)

    with open(args.output, "w") as fh:
        for read_id, seq, qual in reads:
            fh.write(f"@{read_id}\n{seq}\n+\n{qual}\n")

    print(f"Generated {len(reads)} reads → {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
