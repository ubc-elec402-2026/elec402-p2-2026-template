// mkMultBuff.sv -- ELEC 402 2026 Project 2: fill/drain signed 16x16 multiplier buffer.
// Stores products into 64-entry memory (RDY_mult low when full); EN_blockRead & RDY_blockRead drain all 64 in order.
// Active-low synchronous reset (RST_N); latency-insensitive, any multiplier pipeline depth OK.

module mkMultBuff #(parameter N = 32) (
    input logic clk,
    input logic RST_N, // active-low synchronous reset

    // Multiplier / write side
    input logic EN_mult,
    input logic [15:0] mult_input0, // signed operand A (two's complement)
    input logic [15:0] mult_input1, // signed operand B (two's complement)
    output logic RDY_mult,

    // Read / drain side
    input logic EN_blockRead,
    output logic RDY_blockRead,
    output logic VALID_memVal,
    output logic [N-1:0] memVal_data,

    // Memory write port
    output logic EN_writeMem,
    output logic [5:0] writeMem_addr,
    output logic [N-1:0] writeMem_val,

    // Memory read port
    output logic EN_readMem,
    output logic [5:0] readMem_addr,
    input logic [N-1:0] readMem_val
);

    // TODO: implement the fill/drain control logic and instantiate your
    //       pipelined signed multiplier here.

endmodule : mkMultBuff
