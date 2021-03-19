#include "avro/Decoder.hh"
#include "avro/Encoder.hh"
#include "avro/Specific.hh"

namespace c {
struct cpx {
    double re;
    double im;
};

}
namespace avro {
template<> struct codec_traits<c::cpx> {
    static void encode(Encoder& e, const c::cpx& v) {
        avro::encode(e, v.re);
        avro::encode(e, v.im);
    }
    static void decode(Decoder& d, c::cpx& v) {
        avro::decode(d, v.re);
        avro::decode(d, v.im);
    }
};

}

int main()
{
    std::unique_ptr<avro::OutputStream> out = avro::memoryOutputStream(128);
    avro::EncoderPtr e = avro::binaryEncoder();
    e->init(*out);
    c::cpx c1;
    c1.re = 1.0;
    c1.im = 2.13;
    avro::encode(*e, c1);

    std::unique_ptr<avro::InputStream> in = avro::memoryInputStream(*out);
    avro::DecoderPtr d = avro::binaryDecoder();
    d->init(*in);

    c::cpx c2{};
    avro::decode(*d, c2);
    std::cout << '(' << c2.re << ", " << c2.im << ')' << std::endl;
    return 0;
}
