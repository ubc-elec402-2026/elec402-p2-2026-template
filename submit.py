#!/usr/bin/env python3
"""
ELEC 402 Project 2 -- Submission helper

Three checkpoints. Each one stages your work, makes a commit, and pushes a
git tag that the graders look for:

    python3 submit.py start      # START    -- tag your initial commit
    python3 submit.py midpoint   # MIDPOINT -- optional, no-marks feedback check
    python3 submit.py finish     # FINISH   -- your final submission

MIDPOINT is optional and costs no marks. Tag it by 11:59 PM on November 3rd
and we will run the testbench against your RTL and tell you which test cases
are failing, as free feedback -- nothing is deducted for whatever we find.
Skip it if you like; only FINISH is graded.
"""

import subprocess
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

COMMIT_PREFIX = "Project-2-ELEC402"

# Just the RTL -- enough for us to run the functional testbench at MIDPOINT.
RTL_ONLY = {
    "submission/rtl_400":  ["mkMultBuff.sv"],
    "submission/rtl_800": ["mkMultBuff.sv"],
}

# The full submission required at FINISH.
EVERYTHING = {
    **RTL_ONLY,
    "submission/testbench":   ["rtl_checker.sv", "sdf_checker_400.sv", "sdf_checker_800.sv"],
    "submission/scripts":     ["synth.tcl"],
    "submission/syn_reports": ["*.rpt"],
    "submission/outputs":     ["mkMultBuff_400_map.sv", "mkMultBuff_400_map.sdf", "mkMultBuff_400_map.sdc",
                               "mkMultBuff_800_map.sv", "mkMultBuff_800_map.sdf", "mkMultBuff_800_map.sdc",
                               "mkMultBuff_synth_400.dat", "mkMultBuff_synth_800.dat"],
    "submission/pdf_report":  ["report.pdf"],
}

# phase -> (TAG name, required files or None)
PHASES = {
    "start":    ("START",    None),
    "midpoint": ("MIDPOINT", RTL_ONLY),
    "finish":   ("FINISH",   EVERYTHING),
}


def run(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def missing_files(required: dict) -> list[str]:
    missing = []
    for folder, patterns in required.items():
        for pattern in patterns:
            if not list(Path(folder).glob(pattern)):
                missing.append(f"{folder}/{pattern}")
    return missing


def do_phase(phase: str):
    tag, required = PHASES[phase]
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    msg = f"{COMMIT_PREFIX}: {tag}"
    print(f"{tag}  ({date})")

    if phase == "midpoint":
        print(
            "\nMIDPOINT is an optional, no-marks check. We run the testbench against\n"
            "your RTL and send back which test cases fail -- free feedback, nothing\n"
            "deducted. Tag it by 11:59 PM on November 3rd.\n"
        )

    if required:
        miss = missing_files(required)
        if miss:
            print("ERROR: missing required files:")
            for f in miss:
                print(f"  {f}")
            sys.exit(1)
        print("Files to be included:")
        for folder in required:
            for f in sorted(Path(folder).rglob("*")):
                if f.is_file() and f.name != ".gitkeep":
                    print(f"  {f}")

    if input(f"\nTag this commit as {tag} and push? [y/N] ").strip().lower() != "y":
        print("Aborted.")
        sys.exit(0)

    run("git add -A")

    result = run(f'git commit --allow-empty -m "{msg}"')
    if result.returncode != 0:
        print(f"ERROR: commit failed:\n{result.stderr}")
        sys.exit(1)

    result = run(f'git tag -a {tag} -m "{msg}" --force')
    if result.returncode != 0:
        print(f"ERROR: tagging failed:\n{result.stderr}")
        sys.exit(1)

    # push the branch, then (force-)move the tag to this commit
    result = run("git push origin HEAD")
    if result.returncode != 0:
        print(f"ERROR: push failed:\n{result.stderr}")
        print("Make sure you have push access to your repository.")
        sys.exit(1)

    result = run(f"git push origin {tag} --force")
    if result.returncode != 0:
        print(f"ERROR: tag push failed:\n{result.stderr}")
        sys.exit(1)

    print(f"done: commit '{msg}' tagged '{tag}' and pushed")


def main():
    parser = argparse.ArgumentParser(description="ELEC 402 Project 2 submission helper")
    sub = parser.add_subparsers(dest="command")
    for name in PHASES:
        sub.add_parser(name)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    do_phase(args.command)


if __name__ == "__main__":
    main()
