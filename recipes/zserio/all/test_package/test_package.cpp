#include <zserio/BitStreamWriter.h>
#include <zserio/BitStreamReader.h>

int main(int argc, char* argv[])
{
    zserio::BitBuffer bitBuffer(64);
    zserio::BitStreamWriter writer(bitBuffer);
    const uint64_t value = UINT64_MAX;
    writer.writeBits64(value, 64);

    zserio::BitStreamReader reader(writer.getWriteBuffer(), writer.getBitPosition(), zserio::BitsTag());
    const uint64_t readValue = reader.readBits64(64);

    return value == readValue ? 0 : 1;
}
