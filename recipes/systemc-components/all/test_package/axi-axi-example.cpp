#include <array>
#include <axi/axi_initiator.h>
#include <axi/axi_target.h>
#include <axi/scv/recorder_modules.h>
#include <scc.h>
#include <scc/configurable_tracer.h>
#include <scc/memory.h>
#include <scc/hierarchy_dumper.h>
#include <tlm/scc/initiator_mixin.h>
#include <tlm/scc/tlm_gp_shared.h>

using namespace sc_core;
using namespace axi;
using namespace axi::pe;

const unsigned SOCKET_WIDTH = 64;

class testbench : public sc_core::sc_module {
public:
    SC_HAS_PROCESS(testbench);
    sc_core::sc_time clk_period{10, sc_core::SC_NS};
    sc_core::sc_clock clk{"clk", clk_period, 0.5, sc_core::SC_ZERO_TIME, true};
    sc_core::sc_signal<bool> rst{"rst"};
    axi::axi_initiator<SOCKET_WIDTH> intor{"intor"};
    axi::scv::axi_recorder_module<SOCKET_WIDTH> intor_rec{"intor_rec"};
    axi::axi_target<SOCKET_WIDTH> tgt{"tgt"};

private:
    tlm::scc::initiator_mixin<tlm::tlm_initiator_socket<>> top_isck{"top_isck"};
    scc::memory<1_GB> mem{"mem"};

    unsigned id{0};
    unsigned int StartAddr{0};
    unsigned int ResetCycles{10};
    unsigned int BurstLengthByte{16};
    unsigned int NumberOfIterations{8};

public:
    testbench(sc_core::sc_module_name nm)
    : sc_core::sc_module(nm) {
        SC_THREAD(run);
        intor.clk_i(clk);
        top_isck(intor.b_tsck);
        tgt.clk_i(clk);
        intor.isck(intor_rec.tsckt);
        intor_rec.isckt(tgt.tsck);
        tgt.isck(mem.target);
    }

    tlm::tlm_generic_payload* prepare_trans(size_t len) {
        auto trans = tlm::scc::tlm_mm<tlm::tlm_base_protocol_types, false>::get().allocate();
        tlm::scc::tlm_gp_mm::add_data_ptr(len, trans);
        trans->set_data_length(len);
        trans->set_streaming_width(len);
        tlm::scc::setId(*trans, id++);
        return trans;
    }

    void run() {
        rst.write(false);
        for(size_t i = 0; i < ResetCycles; ++i)
            wait(clk.posedge_event());
        rst.write(true);
        wait(clk.posedge_event());
        wait(clk.posedge_event());
        for(int i = 0; i < NumberOfIterations; ++i) {
            SCCDEBUG("testbench") << "executing transactions in iteration " << i;
            { // 1
                tlm::scc::tlm_gp_shared_ptr trans = prepare_trans(BurstLengthByte);
                trans->set_command(tlm::TLM_READ_COMMAND);
                trans->set_address(StartAddr);
                auto delay = SC_ZERO_TIME;
                top_isck->b_transport(*trans, delay);
                if(trans->get_response_status() != tlm::TLM_OK_RESPONSE)
                    SCCERR() << "Invalid response status" << trans->get_response_string();
            }
            StartAddr += BurstLengthByte;
            { // 2
                tlm::scc::tlm_gp_shared_ptr trans = prepare_trans(BurstLengthByte);
                trans->set_command(tlm::TLM_WRITE_COMMAND);
                trans->set_address(StartAddr);
                auto delay = SC_ZERO_TIME;
                top_isck->b_transport(*trans, delay);
                if(trans->get_response_status() != tlm::TLM_OK_RESPONSE)
                    SCCERR() << "Invalid response status" << trans->get_response_string();
            }
            StartAddr += BurstLengthByte;
        }
        wait(100, SC_NS);
        sc_stop();
    }
};

int sc_main(int argc, char* argv[]) {
    sc_report_handler::set_actions(SC_ID_MORE_THAN_ONE_SIGNAL_DRIVER_, SC_DO_NOTHING);
    // clang-format off
    scc::init_logging(
            scc::LogConfig()
            .logLevel(scc::log::WARNING)
            .logAsync(false)
            .coloredOutput(true));
    // clang-format off
    sc_report_handler::set_actions(SC_ERROR, SC_LOG | SC_CACHE_REPORT | SC_DISPLAY);
    scc::configurable_tracer trace("axi_axi_test",
                                   scc::tracer::file_type::TEXT, // define the kind of transaction trace
                                   true,                         // enables vcd
                                   true);
    testbench tb("tb");
    scc::hierarchy_dumper d("axi_axi.elkt", 0);
    try {
        sc_core::sc_start(1_ms);
        SCCINFO() << "Finished";
    } catch(sc_core::sc_report& e) {
        SCCERR() << "Caught sc_report exception during simulation: " << e.what() << ":" << e.get_msg();
    } catch(std::exception& e) {
        SCCERR() << "Caught exception during simulation: " << e.what();
    } catch(...) {
        SCCERR() << "Caught unspecified exception during simulation";
    }
    if(sc_is_running()) {
        SCCERR() << "Simulation timeout!"; // calls sc_stop
    }
    auto errcnt = sc_report_handler::get_count(SC_ERROR);
    auto warncnt = sc_report_handler::get_count(SC_WARNING);
    SCCINFO() << "Finished, there were " << errcnt << " error" << (errcnt == 1 ? "" : "s") << " and " << warncnt
              << " warning" << (warncnt == 1 ? "" : "s");
    return errcnt + warncnt;
}
