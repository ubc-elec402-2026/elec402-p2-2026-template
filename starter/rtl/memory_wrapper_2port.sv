// Memory wrapper to faciliate easy switches between reg memories and PDK provided SRAM Macros. 
// Also use for cross verification b/w macro rtl model and expected registerArray like behavior.
//
// Two-port memories: A = Read port, B = Write Port.
// A : {clkA, aA, cenA, q} -> at posedge(clkA), if cenA == 0, memory at addr 'aA' will be registered to output bus 'q'
// B : {clkB, aB, cenB, d} -> at posedge(clkB), if cenB == 0, memory will store data 'd' at addr 'aB' 
//
// Parameters - 
//      DEPTH: Number of words stored, 
//      WIDTH: word width
//      MEMTYPE: memory type, 0 = Register array.
//      TECHNODE: technology node. Set to 0 if not in use.
//      COL_MUX: column mux, only used for SRAM macros.

module memory_wrapper_2port #(
    parameter DEPTH = 64,
    parameter LOGDEPTH = 6,
    parameter WIDTH = 16,
    parameter MEMTYPE = 0,
    parameter TECHNODE = 0, 
    parameter COL_MUX = 1
    ) ( 
    clkA, aA, cenA, q,
    clkB, aB, cenB, d
    );

input clkA;
input clkB;
input [LOGDEPTH -1:0] aA;
input [LOGDEPTH -1:0] aB;
input cenA;
input cenB;
input [WIDTH -1:0] d;
output [WIDTH -1:0] q;


generate
    if (MEMTYPE == 0) begin : gen_RegArr
        registerArray #( .DEPTH(DEPTH), .LOGDEPTH(LOGDEPTH), .WORDWIDTH(WIDTH)) 
            memInst ( 
                .clkA(clkA), .aA(aA), .cenA(cenA), .q(q), 
                .clkB(clkB), .aB(aB), .cenB(cenB), .d(d)
                    );
    end 
    
    else begin: genMemModule_Error
        $fatal("ERROR: Invalid value for parameter MEMTYPE (%d), DEPTH (%d), WIDTH (%d)", MEMTYPE, DEPTH, WIDTH);
    end
endgenerate

endmodule: memory_wrapper_2port
