#!/usr/bin/env python3
"""
bob.py  --  ELEC 402 2026 Project 2

Run on ssh-soc.ece.ubc.ca. The CMC tool scripts are sourced automatically.

Step-by-step student workflow:

  Step 0 -- copy the synthesis template and fill in its TODOs:
    mkdir -p submission/scripts
    cp starter/scripts/synth.tcl submission/scripts/synth.tcl

  Step 1 -- synthesize 400 MHz design:
    python3 bob.py synth --run 400

  Step 2 -- synthesize 800 MHz design:
    python3 bob.py synth --run 800

  Step 3 -- test your RTL functionally (runs your rtl_checker.sv):
    python3 bob.py check --run 400
    python3 bob.py check --run 800

  Step 4 -- gate-level simulation to generate VCD for power analysis:
    python3 bob.py sim --run 400
    python3 bob.py sim --run 800

  Step 5 -- SDF timing check on the synthesized netlist:
    python3 bob.py timing --run 400
    python3 bob.py timing --run 800

  Step 6 -- power analysis from VCD:
    python3 bob.py power --run 400
    python3 bob.py power --run 800

  Or do everything at once (skips check and timing):
    python3 bob.py all

Submission layout:
    submission/rtl_400/ 400 MHz mkMultBuff + multiplier
    submission/rtl_800/ 800 MHz mkMultBuff + multiplier
    submission/scripts/synth.tcl  synthesis script (copied from starter, TODOs filled in)
    submission/testbench/
        rtl_checker.sv RTL functional checker (top: mkMultBuff_tb)
        sdf_checker_400.sv SDF checker 400 MHz (top: mkMultBuff_sdf_checker_400)
        sdf_checker_800.sv SDF checker 800 MHz (top: mkMultBuff_sdf_checker_800)
"""

import json
import os
import re
import subprocess
import argparse
import sys
from pathlib import Path

# Tool binaries (resolved from PATH after CMC env is loaded)
GENUS_CMD = "genus"
VSIM_CMD  = "vsim"
VLOG_CMD  = "vlog"

# Script paths relative to the project root
SYNTH_TCL = "submission/scripts/synth.tcl"      # student copy of starter/scripts/synth.tcl
POWER_TCL = "starter/scripts/saif2power.tcl"
VCD2SAIF  = "starter/scripts/vcd2saif_run.csh"

# Submission directories (students place their files here)
RTL_DIR_400  = "submission/rtl_400"
RTL_DIR_800 = "submission/rtl_800"
TB_DIR       = "submission/testbench"
STR_DIR      = "starter/rtl"
RPT_DIR      = "submission/syn_reports"
LOG_DIR      = "submission/syn_logs"
OUT_DIR      = "submission/outputs"

# GPDK45 gate-level cell models needed for post-synthesis simulation
LIB_CELLS = (
    "/ubc/ece/data/cmc2/kits/GPDK45/gsclib045_all_v4.4"
    "/gsclib045/verilog/slow_vdd1v0_basicCells.v"
)

# Starter RTL compiled alongside student code (memory model, register array)
PROVIDED_RTL = [
    f"{STR_DIR}/memory_wrapper_2port.sv",
    f"{STR_DIR}/registerArray.sv",
]

# CMC tool environment scripts sourced before running Genus or QuestaSim
CMC_SCRIPTS = [
    "/CMC/scripts/cadence.genus20.10.000.csh",
    "/CMC/scripts/siemens.questasim.2022.1_2.csh",
]


def _load_cmc_env():
    sources = "; ".join(f"source {s}" for s in CMC_SCRIPTS)
    cmd = f"{sources}; python3 -c 'import os,json; print(json.dumps(dict(os.environ)))'"
    r = subprocess.run(["tcsh", "-c", cmd],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       universal_newlines=True)
    if r.returncode != 0:
        print(f"WARNING: could not source CMC tool scripts:\n{r.stderr[:400]}")
        return
    try:
        os.environ.update(json.loads(r.stdout))
    except Exception:
        print("WARNING: failed to parse environment from CMC scripts")


_LICENSE_ERRORS = (
    "Cannot find command filename",
    "license checkout failed",
    "Failed to check out",
    "FATAL: license",
    "Cannot checkout",
)


def run(cmd, desc="", check=True, capture=False):
    print(f"  {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    pipe = subprocess.PIPE if capture else None
    r = subprocess.run(cmd, shell=isinstance(cmd, str),
                       stdout=pipe, stderr=pipe, universal_newlines=True)
    if check and r.returncode != 0:
        print(f"ERROR: {desc or 'command'} failed (exit {r.returncode})")
        if capture:
            print(r.stdout[-3000:])
            print(r.stderr[-1000:])
        sys.exit(1)
    return r


def check_tool(name):
    r = subprocess.run(["which", name], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, universal_newlines=True)
    if r.returncode != 0:
        print(f"ERROR: '{name}' not found in PATH -- source the CMC scripts first")
        sys.exit(1)


def _rtl_dir(tag):
    return RTL_DIR_400 if tag == "400" else RTL_DIR_800


def require_rtl(tag=None):
    tags = [tag] if tag else ["400", "800"]
    for t in tags:
        rtl = Path(_rtl_dir(t)) / "mkMultBuff.sv"
        if not rtl.exists():
            print(f"ERROR: {rtl} not found -- place your {t} MHz implementation there")
            sys.exit(1)


def _fix_module_name(path: Path):
    text = path.read_text()
    fixed = re.sub(r'\bmodule mkMultBuff_\d+\b', 'module mkMultBuff', text)
    fixed = re.sub(
        r'\bmodule mkMultBuff\s*\(',
        'module mkMultBuff #(parameter N = 32) (',
        fixed, count=1,
    )
    if fixed != text:
        path.write_text(fixed)
        print(f"  normalised module name/params in {path}")


def cmd_synth(args):
    tag = getattr(args, 'run', None)
    print(f"=== Synthesis: {tag + ' MHz' if tag else '400 MHz + 800 MHz'} ===")
    check_tool(GENUS_CMD)
    require_rtl(tag)
    if not Path(SYNTH_TCL).exists():
        print(f"ERROR: {SYNTH_TCL} not found -- copy starter/scripts/synth.tcl there "
              f"and fill in its TODOs")
        sys.exit(1)
    Path(RPT_DIR).mkdir(parents=True, exist_ok=True)
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

    preamble = f"set RUN_TAG {tag}; " if tag else ""
    log_path = Path(LOG_DIR) / f"genus_{tag or 'all'}.log"
    print(f"  logging to {log_path}")
    r = subprocess.run(
        [GENUS_CMD, "-batch", "-execute", f"{preamble}source {SYNTH_TCL}"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    log_path.write_text(r.stdout)
    print(r.stdout[-5000:] if len(r.stdout) > 5000 else r.stdout)
    if r.returncode != 0:
        print(f"ERROR: genus synthesis failed (exit {r.returncode})")
        sys.exit(1)

    for t in ([tag] if tag else ["400", "800"]):
        netlist = Path(OUT_DIR) / f"mkMultBuff_{t}_map.sv"
        if netlist.exists():
            _fix_module_name(netlist)

    print(f"reports -> {RPT_DIR}/")
    print(f"logs    -> {LOG_DIR}/")
    print(f"outputs -> {OUT_DIR}/")


def cmd_check(args):
    tags = [args.run] if args.run else ["400", "800"]
    results = []
    for tag in tags:
        print(f"=== RTL check ({tag} MHz) ===")
        results.append(_check_one(tag))
    print(f"=== Overall: {'PASS' if all(results) else 'FAIL'} ===")


def _check_one(tag):
    check_tool(VLOG_CMD)
    check_tool(VSIM_CMD)

    rtl_dir = Path(_rtl_dir(tag))
    if not rtl_dir.exists():
        print(f"ERROR: {rtl_dir} not found")
        return False

    sv_files = list(rtl_dir.glob("*.sv"))
    if not sv_files:
        print(f"ERROR: no .sv files in {rtl_dir}")
        return False

    tb_file = str(Path(TB_DIR) / "rtl_checker.sv")
    top     = "mkMultBuff_tb"
    if not Path(tb_file).exists():
        print(f"ERROR: {tb_file} not found -- copy starter/tb/rtl_checker.sv there")
        return False

    # RTL sim: memory wrappers + student RTL + testbench (no lib cells, no netlist)
    r = run([VLOG_CMD, "-sv"] + PROVIDED_RTL + [str(f) for f in sv_files] + [tb_file],
            desc="vlog", check=False, capture=True)
    if r.returncode != 0:
        print("  COMPILE FAIL")
        print(r.stdout[-2000:])
        return False

    r = run([VSIM_CMD, "-batch", "-do", "run -all; quit -f", f"work.{top}"],
            check=False, capture=True)
    out = r.stdout + r.stderr
    print(out[-4000:])
    passed = "ALL PASS" in out
    print(f"  result: {'PASS' if passed else 'FAIL'}")
    return passed


def cmd_sim(args):
    tag = args.run
    print(f"=== Gate-level sim for power ({tag} MHz) ===")
    check_tool(VLOG_CMD)
    check_tool(VSIM_CMD)

    tb_file = str(Path(TB_DIR) / "rtl_checker.sv")
    if not Path(tb_file).exists():
        print(f"ERROR: {tb_file} not found")
        sys.exit(1)

    netlist  = Path(OUT_DIR) / f"mkMultBuff_{tag}_map.sv"
    vcd_file = Path(OUT_DIR) / f"mkMultBuff_{tag}.vcd"

    if not netlist.exists():
        print(f"ERROR: {netlist} not found -- run synth first")
        sys.exit(1)

    _fix_module_name(netlist)

    sv_files = [str(f) for f in Path(_rtl_dir(tag)).glob("*.sv")]
    run([VLOG_CMD, "-sv", LIB_CELLS] + PROVIDED_RTL + sv_files
        + [str(netlist), tb_file], desc="vlog compile")

    do_cmd = (f"vcd file {vcd_file}; vcd add /mkMultBuff_tb/DUT/*; "
              f"run -all; vcd flush; quit -f")
    run([VSIM_CMD, "-batch", "-voptargs=+acc", "-do", do_cmd, "work.mkMultBuff_tb"],
        desc="vsim gate-level")

    print(f"VCD -> {vcd_file}")


def cmd_timing(args):
    tags = [args.run] if args.run else ["400", "800"]
    results = []
    for tag in tags:
        print(f"=== SDF timing ({tag} MHz) ===")
        results.append(_timing_one(tag))
    print(f"=== Timing overall: {'PASS' if all(results) else 'FAIL'} ===")


def _timing_one(tag):
    check_tool(VLOG_CMD)
    check_tool(VSIM_CMD)

    netlist  = Path(OUT_DIR) / f"mkMultBuff_{tag}_map.sv"
    sdf_file = Path(OUT_DIR) / f"mkMultBuff_{tag}_map.sdf"

    if not netlist.exists():
        print(f"ERROR: {netlist} not found -- run synth first")
        return False
    if not sdf_file.exists():
        print(f"ERROR: {sdf_file} not found -- run synth first")
        return False

    _fix_module_name(netlist)

    tb_file = str(Path(TB_DIR) / f"sdf_checker_{tag}.sv")
    if not Path(tb_file).exists():
        print(f"ERROR: {tb_file} not found -- copy starter/tb/sdf_checker_{tag}.sv there")
        return False

    top = f"mkMultBuff_sdf_checker_{tag}"

    # Gate-level compile: lib cells + memory wrappers + synthesized netlist + testbench.
    # Pre-synthesis RTL is NOT included -- the netlist already contains the full design.
    r = run([VLOG_CMD, "-sv", LIB_CELLS] + PROVIDED_RTL
            + [str(netlist), tb_file],
            desc="vlog SDF compile", check=False, capture=True)
    if r.returncode != 0:
        print("  COMPILE FAIL")
        print(r.stdout[-2000:])
        return False

    r = run([VSIM_CMD, "-batch", f"+sdf_file={sdf_file}", "-voptargs=+acc",
             "-do", "run -all; quit -f", f"work.{top}"],
            check=False, capture=True)
    out = r.stdout + r.stderr
    print(out[-4000:])
    passed = "ALL PASS" in out or "timing closure confirmed" in out
    x_fail = "TIMING FAIL" in out or "TIMING VIOLATIONS" in out
    print(f"  result: {'PASS' if passed else ('TIMING VIOLATION' if x_fail else 'FAIL')}")
    return passed


def _genus_power(tag, db_file):
    if not db_file.exists():
        print(f"  WARNING: {db_file} not found -- skipping Genus power")
        return False
    r = subprocess.run(
        [GENUS_CMD, "-batch",
         "-execute", f"set RUN_NAME {tag}",
         "-execute", f"read_db {db_file}",
         "-files", POWER_TCL],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    combined = r.stdout + r.stderr
    if r.returncode != 0 or any(e in combined for e in _LICENSE_ERRORS):
        snippet = combined[:800].strip()
        if snippet:
            print("  Genus failed:\n    " + "\n    ".join(snippet.splitlines()[:6]))
        return False
    print(r.stdout[-2000:])
    return True


def cmd_power(args):
    tag = args.run
    print(f"=== Power analysis ({tag} MHz) ===")

    vcd_file  = Path(OUT_DIR) / f"mkMultBuff_{tag}.vcd"
    saif_file = Path(OUT_DIR) / f"mkMultBuff_{tag}.saif"
    db_file   = Path(OUT_DIR) / f"mkMultBuff_synth_{tag}.dat"

    if not vcd_file.exists():
        print(f"ERROR: {vcd_file} not found -- run 'bob.py sim --run {tag}' first")
        sys.exit(1)

    print("  VCD -> SAIF ...")
    run(f"csh {VCD2SAIF} {vcd_file} {saif_file}", desc="vcd2saif")

    if _genus_power(tag, db_file):
        print("  Genus power complete.")
    else:
        lib_power = Path("solution/lib_power.py")
        if lib_power.exists():
            LIB_FILE = (
                "/ubc/ece/data/cmc2/kits/GPDK45/gsclib045_all_v4.4"
                "/gsclib045/timing/slow_vdd1v0_basicCells.lib"
            )
            netlist = Path(OUT_DIR) / f"mkMultBuff_{tag}_map.sv"
            rpt     = Path(RPT_DIR) / f"mkMultBuff_{tag}_saif_power.rpt"
            run([sys.executable, str(lib_power),
                 "--netlist", str(netlist), "--saif", str(saif_file),
                 "--lib", LIB_FILE, "--freq", "400e6" if tag == "400" else "800e6",
                 "--out", str(rpt)], desc="lib_power estimate")
        else:
            print("  Genus power unavailable (license server may be down).")
            print(f"  Re-run later: python3 bob.py power --run {tag}")

    rpt = Path(RPT_DIR) / f"mkMultBuff_{tag}_saif_power.rpt"
    if rpt.exists():
        print(f"power report -> {rpt}")


def cmd_all(args):
    args.run = None
    cmd_synth(args)
    for tag in ["400", "800"]:
        args.run = tag
        cmd_sim(args)
        cmd_power(args)


def main():
    _load_cmc_env()
    p = argparse.ArgumentParser(description="ELEC 402 P2 runner")
    sub = p.add_subparsers(dest="command")

    ps = sub.add_parser("synth", help="synthesis (400 MHz, 800 MHz, or both)")
    ps.add_argument("--run", choices=["400", "800"], default=None)

    pc = sub.add_parser("check", help="RTL functional sim")
    pc.add_argument("--run", choices=["400", "800"], default=None)

    ps2 = sub.add_parser("sim", help="gate-level sim (no SDF) -> VCD for power")
    ps2.add_argument("--run", choices=["400", "800"], required=True)

    pt = sub.add_parser("timing", help="SDF-annotated gate-level timing check")
    pt.add_argument("--run", choices=["400", "800"], default=None)

    pp = sub.add_parser("power", help="VCD -> SAIF -> power report")
    pp.add_argument("--run", choices=["400", "800"], required=True)

    sub.add_parser("all", help="synth + sim + power for both frequencies")

    args = p.parse_args()
    {
        "synth":  cmd_synth,
        "check":  cmd_check,
        "sim":    cmd_sim,
        "timing": cmd_timing,
        "power":  cmd_power,
        "all":    cmd_all,
    }.get(args.command, lambda _: p.print_help())(args)


if __name__ == "__main__":
    main()
