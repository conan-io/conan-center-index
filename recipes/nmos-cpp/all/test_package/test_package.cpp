#include <fstream>
#include <thread>
#include "cpprest/json_utils.h"
#include "nmos/id.h"
#include "nmos/log_gate.h"
#include "nmos/model.h"
#include "nmos/node_resource.h"
#include "nmos/node_server.h"
#include "nmos/server.h"

const web::json::field_with_default<int64_t> how_long{ U("how_long"), 2000 };

int main(int argc, char* argv[])
{
    nmos::node_model node_model;
    nmos::experimental::log_model log_model;
    nmos::experimental::log_gate gate(std::cerr, std::cout, log_model);
    nmos::experimental::node_implementation node_implementation;

    if (argc > 1)
    {
        std::ifstream file(argv[1]);
        node_model.settings = web::json::value::parse(file);
    }
    nmos::insert_node_default_settings(node_model.settings);

    auto node_server = nmos::experimental::make_node_server(node_model, node_implementation, log_model, gate);
    nmos::insert_resource(node_model.node_resources, nmos::make_node(nmos::make_id(), node_model.settings));

    try
    {
        nmos::server_guard node_server_guard(node_server);
        std::this_thread::sleep_for(std::chrono::milliseconds(how_long(node_model.settings)));
    }
    catch (const std::exception& e)
    {
        slog::log<slog::severities::error>(gate, SLOG_FLF) << "Exception: " << e.what();
    }
    return 0;
}
