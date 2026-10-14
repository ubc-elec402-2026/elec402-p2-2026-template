# synth.tcl - Cadence Genus synthesis template, ELEC 402 2026
# Copy to submission/scripts/synth.tcl, fill in every TODO, run with: python3 bob.py synth --run 400 | 800
# Do not rename the output files: bob.py and the SDF / power steps look for them by name.

set TOP_LEVEL    mkMultBuff
set RTL_DIR_400  ./submission/rtl_400
set RTL_DIR_800  ./submission/rtl_800
set STR_DIR      ./starter/rtl
set RPT_DIR      ./submission/syn_reports
set OUT_DIR      ./submission/outputs
set LIB_PATH     /ubc/ece/data/cmc2/kits/GPDK45/gsclib045_all_v4.4/gsclib045/timing

sh mkdir -p $RPT_DIR $OUT_DIR

set_db lib_search_path [concat [get_db lib_search_path] $LIB_PATH]
set_db library "slow_vdd1v0_basicCells.lib"

# tag is the target frequency, 400 or 800. It names the output files.
#### TODO 0: add the other arguments synth_run needs (the code below also uses $rtl_dir).
proc synth_run {tag} {
    global TOP_LEVEL STR_DIR RPT_DIR OUT_DIR

    set RTL_FILES [list $STR_DIR/memory_wrapper_2port.sv $STR_DIR/registerArray.sv]
    foreach f [glob -nocomplain $rtl_dir/*.sv] { lappend RTL_FILES $f }
    foreach f $RTL_FILES { read_hdl -sv $f }
    elaborate $TOP_LEVEL
    set cur [lindex [get_db designs .name] end]
    current_design $cur

    #### TODO 1: clock and input drive (see README "Synthesis > Constraints")

    #### TODO 2: output load

    #### TODO 3: input and output delays

    #### TODO 4: synthesize, optimize, and enable retiming

    #### TODO 5: re-define the clock at the graded period for the reports

    report_area   > $RPT_DIR/${TOP_LEVEL}_${tag}_area.rpt
    report_gates  > $RPT_DIR/${TOP_LEVEL}_${tag}_gates.rpt
    report_timing > $RPT_DIR/${TOP_LEVEL}_${tag}_timing.rpt
    report_power  > $RPT_DIR/${TOP_LEVEL}_${tag}_power.rpt
    report_qor    > $RPT_DIR/${TOP_LEVEL}_${tag}_qor.rpt

    write_hdl -mapped > $OUT_DIR/${TOP_LEVEL}_${tag}_map.sv
    write_sdf         > $OUT_DIR/${TOP_LEVEL}_${tag}_map.sdf
    write_sdc         > $OUT_DIR/${TOP_LEVEL}_${tag}_map.sdc
    write_db -to        $OUT_DIR/${TOP_LEVEL}_synth_${tag}.dat

    puts "done: $tag"
}

# bob.py sets RUN_TAG (from --run) and then sources this script. Work out how to use it.
if {![info exists RUN_TAG]} { set RUN_TAG "all" }

#### TODO 6: call synth_run for each target. Reports are graded at 2.5 ns (400 MHz) and 1.25 ns (800 MHz).
if {$RUN_TAG eq "400" || $RUN_TAG eq "all"} {
}

if {$RUN_TAG eq "800" || $RUN_TAG eq "all"} {
}

puts "synthesis complete - reports in $RPT_DIR"
