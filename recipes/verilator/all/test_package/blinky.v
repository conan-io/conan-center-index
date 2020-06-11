////////////////////////////////////////////////////////////////////////////////
//
// Filename: 	blinky.v
//
// Project:	Verilog Tutorial Example file
//
// Purpose:	Blinks an LED
//
// Creator:	Dan Gisselquist, Ph.D.
//		Gisselquist Technology, LLC
//
////////////////////////////////////////////////////////////////////////////////
//
// Written and distributed by Gisselquist Technology, LLC
//
// This program is hereby granted to the public domain.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY or
// FITNESS FOR A PARTICULAR PURPOSE.
//
////////////////////////////////////////////////////////////////////////////////
//
//
`default_nettype	none
//
module blinky(i_clk, o_led);
`ifdef	VERILATOR
	parameter	WIDTH = 12;
`else
	parameter	WIDTH = 27;
`endif
	input	wire	i_clk;
	output	wire	o_led;

	reg	[WIDTH-1:0]	counter;

	always @(posedge i_clk)
		counter <= counter + 1'b1;

	assign	o_led = counter[WIDTH-1];
endmodule

