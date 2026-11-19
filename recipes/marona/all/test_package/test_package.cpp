#include <marona/mcp.hpp>
#include <cstdlib>

int main() {
    marona::Agent agent;
    agent.client = std::make_shared<marona::Marona>("package-test-key");
    agent.protocols = {std::make_shared<marona::B2A>(
        std::make_shared<marona::B2ACodec>("https://neural.example", "package-test-token"),
        "text")};
    if (agent.protocols.front()->name() != "b2a") return EXIT_FAILURE;
    const marona::D2AMessage data("sensor", {
        {"kind", "data"},
        {"content", marona::Json::array({{{"type", "text"}, {"data", "Ready"}}})}
    });
    marona::validate_message(data.to_json(), "d2a");
    marona::validate_schema({{"type", "integer"}}, 4);
    marona::MCPServer server("Greeting Tools", "greeting-tools", "Greeting tools.", "Tools");
    server.tool({.name = "greet", .description = "Return a greeting."},
        [](const marona::Json&) { return marona::Json{{"greeting", "Hello"}}; });
    const auto reply = server.handle({{"jsonrpc", "2.0"}, {"id", 1},
        {"method", "tools/call"}, {"params", {{"name", "greet"}, {"arguments", marona::Json::object()}}}});
    return reply.contains("result") ? EXIT_SUCCESS : EXIT_FAILURE;
}
