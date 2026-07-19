#include <string>
#include <vector>

#include <NFIR/nfir_lib.h>

int main()
{
    std::vector<uint8_t> src = {'P','5','\n','1',' ','1','\n','2','5','5','\n',128,128};

    uint8_t *tgt = nullptr;
    uint32_t w = 1, h = 1;
    size_t sz = src.size();
    std::vector<std::string> chunks, log;

    NFIR::resample(src.data(), &tgt, 300, 500, "inch", "bicubic", "Gaussian", &w, &h, &sz, "pgm", "pgm", chunks, log);

    return 0;
}
