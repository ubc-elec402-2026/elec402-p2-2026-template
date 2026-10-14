# saif2power.tcl - SAIF-annotated power report, ELEC 402 2026. Called by bob.py as:
#   genus -batch \
#     -x "set RUN_NAME 400" \
#     -x "read_db submission/outputs/mkMultBuff_synth_400.dat" \
#     -files starter/scripts/saif2power.tcl

set TOP_LEVEL mkMultBuff
set RPT_DIR   ./submission/syn_reports

set SAIF_FILE "./submission/outputs/${TOP_LEVEL}_${RUN_NAME}.saif"
set RPT_FILE  "${RPT_DIR}/${TOP_LEVEL}_${RUN_NAME}_saif_power.rpt"

sh mkdir -p $RPT_DIR

# Checker TB instantiates the DUT as: mkMultBuff_tb/DUT
read_saif -instance mkMultBuff_tb/DUT -scale 1 $SAIF_FILE

report_power > $RPT_FILE
puts "SAIF-annotated power report: $RPT_FILE"
