#include <cstdlib>
#include <iostream>
#include <vector>

#include <up-cpp/uuid/factory/Uuidv8Factory.h>
#include <up-cpp/uuid/serializer/UuidSerializer.h>

using namespace uprotocol::uuid;
using namespace uprotocol::v1;

int main(void) {

    UUID uuId = Uuidv8Factory::create();
    std::vector<uint8_t> vectUuid = UuidSerializer::serializeToBytes(uuId);
    UUID uuIdFromByteArr = UuidSerializer::deserializeFromBytes(vectUuid);

    std::string str = "0080b636-8303-8701-8ebe-7a9a9e767a9f";
    UUID uuIdNew = UuidSerializer::deserializeFromString(str);

    return EXIT_SUCCESS;
}
