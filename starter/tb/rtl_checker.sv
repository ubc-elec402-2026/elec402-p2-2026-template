// rtl_checker.sv -- ELEC 402 2026 Project 2. Top: mkMultBuff_tb. Copy to submission/testbench/.
// The harness below wires the DUT to the memory and makes a clock (CLK_HALF_NS 1.25 = 400 MHz, 0.625 = 800 MHz).
// Drive fill/drain, scoreboard every product read out. See README "Testbench requirements" for what to cover.

`timescale 1ns/1ps

module mkMultBuff_tb #(
    parameter real CLK_HALF_NS = 1.25,
    parameter int  N = 32
);

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
        .EN_mult(EN_mult),
        .mult_input0(mult_input0), .mult_input1(mult_input1),
        .RDY_mult(RDY_mult),
        .EN_blockRead(EN_blockRead), .RDY_blockRead(RDY_blockRead),
        .VALID_memVal(VALID_memVal), .memVal_data(memVal_data),
        .EN_writeMem(EN_writeMem), .writeMem_addr(writeMem_addr),
        .writeMem_val(writeMem_val),
        .EN_readMem(EN_readMem), .readMem_addr(readMem_addr),
        .readMem_val(readMem_val)
    );

    // The memory belongs to the testbench, not to mkMultBuff.
    memory_wrapper_2port #(
        .DEPTH(64), .LOGDEPTH(6), .WIDTH(N), .MEMTYPE(0)
    ) MEM (
        .clkA(clk), .aA(readMem_addr), .cenA(~EN_readMem), .q(readMem_val),
        .clkB(clk), .aB(writeMem_addr), .cenB(~EN_writeMem), .d(writeMem_val)
    );

    initial clk = 0;
    always #(CLK_HALF_NS * 1ns) clk = ~clk;

    // Optional SDF back-annotation hook (used by the SDF checker flow).
    initial begin
        string sdf_path;
        if ($value$plusargs("sdf_file=%s", sdf_path))
            $sdf_annotate(sdf_path, DUT, , , "MAXIMUM");
    end

    initial begin
        // TODO: reset, fill the memory with signed products, drain and check,
        //       print "ALL PASS" on success. bob.py greps for "ALL PASS".
        $display("TODO: implement rtl_checker");
        $finish;
    end

endmodule
