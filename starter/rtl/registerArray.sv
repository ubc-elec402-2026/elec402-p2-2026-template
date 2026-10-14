// Register Array for implementing small memories. 
//  Usually synthesized when DEPTH*WORDWIDTH < 100
//
// Parameters DEPTH: Number of words stored, WIDTH: word width
//
// Interfaces : A - read port, B - write port
// A : {clkA, aA, cenA, q} -> at posedge(clkA), if cenA == 0, memory at addr 'aA' will be registered to output bus 'q'
// B : {clkB, aB, cenB, d} -> at posedge(clkB), if cenB == 0, memory will store data 'd' at addr 'aB' 

module registerArray #(
    parameter DEPTH = 64,
    parameter LOGDEPTH = 6,
    parameter WORDWIDTH = 16
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
input [WORDWIDTH -1:0] d;
output [WORDWIDTH -1:0] q;

localparam [WORDWIDTH -1:0] ZERO_DATA = {WORDWIDTH{1'b0}};
localparam [LOGDEPTH -1:0] ZERO_ADDR = {LOGDEPTH{1'b0}};
localparam [LOGDEPTH -1:0] MAX_ADDR = {LOGDEPTH{1'b1}};

reg [WORDWIDTH -1:0] regArray [DEPTH -1:0];
reg [WORDWIDTH -1:0] rowBuffer;

always @(posedge clkA) begin
    if (~cenA) begin
        rowBuffer <= regArray[aA];
    end
end

always @(posedge clkB) begin
    if (~cenB) begin
        regArray[aB] <= d;
    end
end

assign q = rowBuffer;

endmodule: registerArray
