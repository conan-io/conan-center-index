#include "lsl_cpp.h"

#include <iostream>
#include <vector>

int main() {
    std::cout << "Resolving streams..." << std::endl;
    std::vector<lsl::stream_info> streams = lsl::resolve_streams();
    std::cout << streams.size() << " streams found:" << std::endl;
    for (auto &stream : streams) {
        std::cout << stream.as_xml() << std::endl;
    }
    return 0;
}
