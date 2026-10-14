// sdf_checker_800.sv -- ELEC 402 2026 Project 2 (REVISED). 800 MHz SDF checker.
// Top module must stay mkMultBuff_sdf_checker_800. Clock fixed at 1.25 ns.
// bob.py passes +sdf_file=submission/outputs/mkMultBuff_800_map.sdf at run time.
// An X on memVal_data after VALID_memVal means a timing violation in your netlist.
//
// Copy to submission/testbench/ and write your gate-level fill/drain checker.
// Tip: launch (drive) your inputs on the rising edge, but sample the outputs on the falling edge instead of the rising edge.

`timescale 1ns/1ps

module mkMultBuff_sdf_checker_800;

    localparam real HALF_NS = 0.625;  // 1.25 ns period -> 800 MHz
    localparam int  N = 32;

    logic clk, RST_N;
    logic EN_mult;
    logic [15:0] mult_input0, mult_input1;
    logic RDY_mult;
    logic EN_blockRead;
    logic RDY_blockRead;
    logic VALID_memVal;
    logic [N-1:0] memVal_data;
    logic EN_writeMem, EN_readMem;
    logic [5:0] writeMem_addr, readMem_addr;
    logic [N-1:0] writeMem_val, readMem_val;

    mkMultBuff #(.N(N)) DUT (
        .clk(clk), .RST_N(RST_N),
        .EN_mult(EN_mult), .mult_input0(mult_input0), .mult_input1(mult_input1),
        .RDY_mult(RDY_mult),
        .EN_blockRead(EN_blockRead), .RDY_blockRead(RDY_blockRead),
        .VALID_memVal(VALID_memVal),
        .memVal_data(memVal_data),
        .EN_writeMem(EN_writeMem), .writeMem_addr(writeMem_addr),
        .writeMem_val(writeMem_val),
        .EN_readMem(EN_readMem), .readMem_addr(readMem_addr),
        .readMem_val(readMem_val)
    );

    memory_wrapper_2port #(.DEPTH(64), .LOGDEPTH(6), .WIDTH(N), .MEMTYPE(0)) MEM (
        .clkA(clk), .aA(readMem_addr), .cenA(~EN_readMem), .q(readMem_val),
        .clkB(clk), .aB(writeMem_addr), .cenB(~EN_writeMem), .d(writeMem_val)
    );

    initial clk = 0;
    always #(HALF_NS * 1ns) clk = ~clk;

    initial begin
        string sdf_path;
        if ($value$plusargs("sdf_file=%s", sdf_path))
            $sdf_annotate(sdf_path, DUT, , , "MAXIMUM");
    end

    initial begin
        // TODO: fill/drain the memory under SDF annotation; flag any X on
        //       memVal_data as a timing violation; print "ALL PASS" on success.
        $display("TODO: implement sdf_checker_800");
        $finish;
    end

endmodule : mkMultBuff_sdf_checker_800
