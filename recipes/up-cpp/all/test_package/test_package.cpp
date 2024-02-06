#include <cstdlib>
#include <up-cpp/uri/serializer/LongUriSerializer.h>

using namespace uprotocol::v1;
using namespace uprotocol::uri;

int main(void) {

    auto uri = LongUriSerializer::deserialize("/test.app/1/milliseconds");
    auto uriStr = LongUriSerializer::serialize(timeUri);

    std::cout << "serialized " << uriStr << std::endl;
    return EXIT_SUCCESS;
}
