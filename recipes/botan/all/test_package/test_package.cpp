#include <botan/hex.h>

int main()
{
    std::vector<uint8_t> key = Botan::hex_decode("000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F");
    return 0;
}
