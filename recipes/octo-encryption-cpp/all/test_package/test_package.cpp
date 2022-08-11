#include "octo-encryption-cpp/encryptors/encrypted-string.hpp"
#include "octo-encryption-cpp/encryptors/ssl/ssl-encryptor.hpp"
#include "octo-encryption-cpp/encryptors/materials/simple-material.hpp"

int main(int argc, char** argv)
{
    octo::encryption::SingleEncryptedString encrypted_string(encryptor);
    // Encryption
    encrypted_string.set(input_plain_string, material);
    octo::encryption::SingleEncryptedString encrypted_string2(encrypted_string.cipher(), material, encryptor);
    // Decryption
    const std::string& output_plain_string = encrypted_string2.get();
    encrypted_string2.destruct();
}