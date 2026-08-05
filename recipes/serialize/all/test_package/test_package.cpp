#include <serialize.h>

#include <cstdint>
#include <cstdio>

struct TestObject
{
    int a;
    uint32_t b;
    bool c;

    template <typename Stream> bool Serialize( Stream & stream )
    {
        serialize_int( stream, a, -100, 100 );
        serialize_bits( stream, b, 23 );
        serialize_bool( stream, c );
        return true;
    }
};

int main()
{
    // WriteStream requires the buffer size to be a multiple of 8, and ReadStream
    // requires the allocation to extend past the encoded data; 256 covers both.
    uint8_t buffer[256];

    TestObject in;
    in.a = -5;
    in.b = 12345;
    in.c = true;

    serialize::WriteStream writeStream( buffer, sizeof(buffer) );
    if ( !in.Serialize( writeStream ) )
        return 1;
    writeStream.Flush();

    TestObject out;
    serialize::ReadStream readStream( buffer, writeStream.GetBytesProcessed() );
    if ( !out.Serialize( readStream ) )
        return 1;

    if ( out.a != in.a || out.b != in.b || out.c != in.c )
        return 1;

    printf( "serialize %s: round trip ok\n", SERIALIZE_VERSION );
    return 0;
}

