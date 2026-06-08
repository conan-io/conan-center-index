#include <iostream>
#include <DaggyCore/Core.hpp>
#include <DaggyCore/Sources.hpp>

namespace {
constexpr const char* json_data = R"JSON(
{
    "sources": {
        "localhost" : {
            "type": "local",
            "commands": {
                "ping1": {
                    "exec": "ping 127.0.0.1",
                    "extension": "log"
                },
                "ping2": {
                    "exec": "ping 127.0.0.1",
                    "extension": "log"
                }
            }
        }
    }
}
)JSON";
}

int main(int argc, char** argv)
{
    daggy::Core core(*daggy::sources::convertors::json(json_data));
    const auto& version = core.version();
    std::cout << "Daggy Version: " << version.major << "." << version.minor << "." << version.patch << std::endl;
    return 0;
}
