#include "plusaes/plusaes.hpp"

#include <string>
#include <vector>

int main() {
    // AES-CBC 128-bit

    // parameters
    const std::string raw_data = "Hello, plusaes";
    const std::vector<unsigned char> key = plusaes::key_from_string(&"EncryptionKey128"); // 16-char = 128-bit
    const unsigned char iv[16] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
    };

    // encrypt
    const unsigned long encrypted_size = plusaes::get_padded_encrypted_size(raw_data.size());
    std::vector<unsigned char> encrypted(encrypted_size);

    plusaes::encrypt_cbc((unsigned char*)raw_data.data(), raw_data.size(), &key[0], key.size(), &iv, &encrypted[0], encrypted.size(), true);
    // fb 7b ae 95 d5 0f c5 6f 43 7d 14 6b 6a 29 15 70

    // decrypt
    unsigned long padded_size = 0;
    std::vector<unsigned char> decrypted(encrypted_size);

    plusaes::decrypt_cbc(&encrypted[0], encrypted.size(), &key[0], key.size(), &iv, &decrypted[0], decrypted.size(), &padded_size);
    // Hello, plusaes
}
