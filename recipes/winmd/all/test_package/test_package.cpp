#include <cstdlib>
#include <winmd_reader.h>


int main(void) {
    std::vector<std::string> include = { "N1", "N3", "N3.N4.N5" };
    std::vector<std::string> exclude = { "N2", "N3.N4" };

    winmd::reader::filter f{ include, exclude };

    return f.empty() ? EXIT_FAILURE : EXIT_SUCCESS;
}
