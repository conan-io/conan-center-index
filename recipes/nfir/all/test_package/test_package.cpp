#include <fstream>
#include <vector>
#include <string>

#include <NFIR/nfir_lib.h>

int main()
{

    const auto loadFile = [](const char *path)
    {
        std::ifstream s(path, std::ios::binary | std::ios::ate);
        std::vector<uint8_t> data(s.tellg());
        s.seekg(0);
        s.read(reinterpret_cast<char *>(data.data()), data.size());
        return data;
    };

    std::vector<std::string> logRuntime;
    std::vector<std::string> vecPngTextChunk;

    NFIR::resample(loadFile("image.png"),
                   1000, 500, "inch",
                   "bilinear", "Gaussian",
                   "png", "png", vecPngTextChunk,
                   logRuntime);

    return 0;
}
