# runSim_syn.tcl - QuestaSim gate-level simulation, ELEC 402 2026 Project 2
# bob.py runs this with vsim -batch. Interactive: set RUN_NAME 400 (or 800), then do starter/scripts/runSim_syn.tcl

if {![info exists RUN_NAME]} { set RUN_NAME 400 }

set TOP_LEVEL mkMultBuff
set TB_NAME   mkMultBuff_tb
set SDF_FILE  ./submission/outputs/${TOP_LEVEL}_${RUN_NAME}_map.sdf
set VCD_FILE  ./submission/outputs/${TOP_LEVEL}_${RUN_NAME}.vcd

# Launch simulation with SDF back-annotation
vsim -default_radix signed \
     -voptargs=+acc \
     -sdfnoerror \
     -sdfmax /$TB_NAME/DUT=$SDF_FILE \
     -l submission/outputs/${TB_NAME}_${RUN_NAME}.sim.log \
     work.$TB_NAME

# VCD dump for power analysis (feed to vcd2saif_run.csh afterwards)
vcd file $VCD_FILE
vcd add /$TB_NAME/DUT/*

# Waveforms (interactive only - skipped in -batch)
add wave -label CLK -position insertpoint sim:/$TB_NAME/DUT/clk

add wave -divider "Multiply Interface"
add wave -label EN_mult    -position insertpoint sim:/$TB_NAME/DUT/EN_mult
add wave -label RDY_mult   -position insertpoint sim:/$TB_NAME/DUT/RDY_mult

add wave -divider "Write to Memory"
add wave -label EN_writeMem   -position insertpoint sim:/$TB_NAME/DUT/EN_writeMem
add wave -label writeMem_addr -position insertpoint sim:/$TB_NAME/DUT/writeMem_addr
add wave -label writeMem_val  -position insertpoint sim:/$TB_NAME/DUT/writeMem_val

add wave -divider "Read Interface"
add wave -label EN_blockRead -position insertpoint sim:/$TB_NAME/DUT/EN_blockRead
add wave -label RDY_blockRead -position insertpoint sim:/$TB_NAME/DUT/RDY_blockRead
add wave -label EN_readMem   -position insertpoint sim:/$TB_NAME/DUT/EN_readMem
add wave -label readMem_addr -position insertpoint sim:/$TB_NAME/DUT/readMem_addr

add wave -divider "Output"
add wave -label VALID_memVal -position insertpoint sim:/$TB_NAME/DUT/VALID_memVal
add wave -label memVal_data  -position insertpoint sim:/$TB_NAME/DUT/memVal_data

run -all
vcd flush
