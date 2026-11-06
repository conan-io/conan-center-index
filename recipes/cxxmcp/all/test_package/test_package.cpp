#include <cxxmcp/sdk.hpp>

int main() {
    mcp::ServerPeer server;
    return server.list_prompts().empty() ? 0 : 1;
}
