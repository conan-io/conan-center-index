#include <curvepress/curvepress.hpp>
#include <cstdint>
#include <cstdio>
#include <vector>

int main() {
    // Collinear points — RDP drops all interior points, keeps only first and last
    std::vector<int64_t> ts {0, 1'000'000, 2'000'000, 3'000'000, 4'000'000};
    std::vector<double>  val{0.0, 1.0, 2.0, 3.0, 4.0};
    auto data = curvepress::compress_rdp(ts, val, 0.1);
    auto dec  = curvepress::decompress(data);
    std::printf("curvepress %s: %zu -> %zu points\n",
                curvepress::version(), ts.size(), dec.timestamps_ns.size());
}
