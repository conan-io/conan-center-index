#include <azure/core.hpp>

#include <string>
#include <vector>

int main()
{
  std::vector<uint8_t> data = {1, 2, 3, 4};
  Azure::Core::IO::MemoryBodyStream stream(data);

  // Hash through the public API so that the crypto backend
  // (bcrypt on Windows, OpenSSL elsewhere) is linked and exercised.
  const std::string text = "abc";
  Azure::Core::Cryptography::Md5Hash md5;
  const std::vector<uint8_t> hash
      = md5.Final(reinterpret_cast<const uint8_t*>(text.data()), text.size());

  return Azure::Core::Convert::Base64Encode(hash) == "kAFQmDzST7DWlj99KOF/cg==" ? 0 : 1;
}
