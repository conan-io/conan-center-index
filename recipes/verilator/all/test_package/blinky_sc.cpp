#include "Vblinky.h"
#include "verilated.h"
#include "verilated_vcd_c.h"

#include <systemc>

#include <iostream>

SC_MODULE(BlinkyTop)
{
    sc_in<bool> clk;
    sc_signal<bool> led;

    Vblinky blinky;

    void led_monitor() {
        std::cout << sc_time_stamp() << ": led = " << led << "\n";
    }

    SC_CTOR(BlinkyTop)
    : clk("clk")
    , led("led")
    , blinky("blinky") {
        blinky.i_clk(clk);
        blinky.o_led(led);

        SC_METHOD(led_monitor);
        sensitive << led;
    }
};

int main(int argc, char **argv) {
    sc_clock clk("clk", sc_time(1, SC_NS), 0.5);

    BlinkyTop top("top");
    top.clk(clk);

    sc_start(sc_time(1<<20, SC_NS));
}
