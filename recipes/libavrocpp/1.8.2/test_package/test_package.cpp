#include "avro/Decoder.hh"
#include "avro/Encoder.hh"
#include "avro/Specific.hh"

#include <memory>

int main()
{
    int64_t dummy = 1234;
    std::unique_ptr<avro::OutputStream> out = avro::memoryOutputStream();
    avro::EncoderPtr e = avro::binaryEncoder();
    e->init(*out);
    avro::encode(*e, dummy);

    std::unique_ptr<avro::InputStream> in = avro::memoryInputStream(*out);
    avro::DecoderPtr d = avro::binaryDecoder();
    d->init(*in);

    int64_t decoded;
    avro::decode(*d, decoded);

    if (dummy != decoded)
    {
        return 1;
    }
    return 0;
}
