#include <nop/serializer.h>
#include <nop/utility/stream_writer.h>

#include <iostream>
#include <map>
#include <sstream>
#include <utility>
#include <vector>

int main() {
    using Writer = nop::StreamWriter<std::stringstream>;
    nop::Serializer<Writer> serializer;

    serializer.Write(std::vector<int>{1, 2, 3, 4});
    serializer.Write(std::vector<std::string>{"foo", "bar", "baz"});

    using MapType = std::map<std::uint32_t, std::pair<std::uint64_t, std::string>>;
    serializer.Write(MapType{{0, {10, "foo"}}, {1, {20, "bar"}}, {2, {30, "baz"}}});

    const std::string data = serializer.writer().stream().str();
    std::cout << "Wrote " << data.size() << " bytes." << std::endl;
    return 0;
}
