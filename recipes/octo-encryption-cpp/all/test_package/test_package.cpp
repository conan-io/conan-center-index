#include "octo-encryption-cpp/encryptors/encrypted-string.hpp"
#include "octo-encryption-cpp/encryptors/ssl/ssl-encryptor.hpp"
#include "octo-encryption-cpp/encryptors/materials/simple-material.hpp"

int main(int argc, char** argv)
{
    auto encryptor = std::make_shared<octo::encryption::ssl::SSLEncryptor>(
        std::make_shared<octo::encryption::ssl::SSLCipher>("AES256"));
    auto material = std::make_shared<octo::encryption::SimpleMaterial>(std::vector<std::string>{"Key1", "Key2", "Key3"});
    octo::encryption::SingleEncryptedString encrypted_string(encryptor);
    // Encryption
    encrypted_string.set("some_string", material);
    octo::encryption::SingleEncryptedString encrypted_string2(encrypted_string.cipher(), material, encryptor);
    // Decryption
    const std::string& output_plain_string = encrypted_string2.get();
    encrypted_string2.destruct();
}
