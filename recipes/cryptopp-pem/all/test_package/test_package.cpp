#include <cryptopp/pem.h>

#include <iostream>
#include <string>

int main()
{
    try
    {
        CryptoPP::RSA::PublicKey publicKey;
        std::string key = R"(-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDWEDeqk749sYZAt2adT2m1Vo8N
h86GzAs/ZWvlQDUyiedDuAvOhrVwllp4GuAXP7tZwGoeJ+Un6Nkl45IIQ2U9NMWQ
aru76CD9kVUdThnKVOaeeqZysM1Bz6iJF5piSUzVKZdEk6rIUZjrwpNaYdBBq4a/
cNETdvolooljIRB8ywIDAQAB
-----END PUBLIC KEY-----)";
        CryptoPP::StringSource source_str{key, true};
        CryptoPP::PEM_Load(source_str, publicKey);

        return 0;
    }
    catch(const std::exception& e)
    {
        std::cout << e.what() << std::endl;
        return 1;
    }
}
