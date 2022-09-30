#include "fastpfor/codecfactory.h"
#include "fastpfor/deltautil.h"

int main() {
  using namespace FastPForLib;

  IntegerCODEC &codec = *CODECFactory::getFromName("simdfastpfor256");

  size_t N = 10 * 1000;
  std::vector<uint32_t> mydata(N);
  for (uint32_t i = 0; i < N; i += 150)
    mydata[i] = i;

  std::vector<uint32_t> compressed_output(N + 1024);

  size_t compressedsize = compressed_output.size();
  codec.encodeArray(mydata.data(), mydata.size(), compressed_output.data(),
                    compressedsize);

  compressed_output.resize(compressedsize);
  compressed_output.shrink_to_fit();

  std::cout << std::setprecision(3);
  std::cout << "You are using "
            << 32.0 * static_cast<double>(compressed_output.size()) /
                   static_cast<double>(mydata.size())
            << " bits per integer. " << std::endl;

  return 0;
}
