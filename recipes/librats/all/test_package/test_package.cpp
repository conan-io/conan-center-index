/**
 * Smoke test for the packaged library: compiles against the installed headers and
 * links against the installed binary.
 *
 * Its real job is to be the canary for the shared build. On MSVC a public class
 * that was never marked RATS_API (src/util/rats_export.h) is simply absent from
 * the DLL — it links fine in the static build and fails only at a downstream
 * consumer. So this touches one out-of-line member of each exported type rather
 * than just constructing a Node.
 *
 * Nothing here opens a socket: subsystems are attached but the node is never
 * started, which is enough to force the linker to resolve their symbols.
 */

#include <librats/node/node.h>
#include <librats/subsystems/dht_discovery.h>
#include <librats/subsystems/file_transfer.h>
#include <librats/subsystems/mdns_discovery.h>
#include <librats/subsystems/message_json.h>
#include <librats/subsystems/peer_exchange.h>
#include <librats/subsystems/ping_service.h>
#include <librats/subsystems/port_mapping_service.h>
#include <librats/subsystems/pubsub.h>
#include <librats/subsystems/reconnection.h>
#include <librats/util/json.h>

#include <cstdio>
#include <memory>

int main() {
    librats::NodeConfig config;
    config.listen_port = 0;  // ephemeral
    librats::Node node(config);

    // Every opt-in subsystem, so a missing export on any of them breaks the build.
    node.add_subsystem(std::make_unique<librats::DhtDiscovery>(librats::DhtDiscovery::Config{}));
    node.add_subsystem(std::make_unique<librats::MdnsDiscovery>());
    node.add_subsystem(std::make_unique<librats::PubSub>());
    node.add_subsystem(std::make_unique<librats::FileTransfer>("."));
    node.add_subsystem(std::make_unique<librats::MessageJson>());
    node.add_subsystem(std::make_unique<librats::PingService>());
    node.add_subsystem(std::make_unique<librats::PeerExchange>());
    node.add_subsystem(std::make_unique<librats::PortMappingService>());
    node.add_subsystem(std::make_unique<librats::ReconnectionService>());

    // Value types that cross the boundary by value.
    const auto address = librats::Address::parse("127.0.0.1:4242");
    if (!address || !address->is_valid()) {
        std::fputs("librats: Address::parse failed\n", stderr);
        return 1;
    }

    const librats::Json doc = librats::Json::parse(R"({"ok":true})");

    std::printf("librats peer id: %s  peers: %zu  addr: %s  json: %s\n",
                node.local_id().short_hex().c_str(),
                node.peer_count(),
                address->to_string().c_str(),
                doc.dump().c_str());
    return 0;
}
