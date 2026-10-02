#include "ironpress.hpp"

#include <cstdlib>
#include <string_view>

int main() {
    const auto pdf = ironpress::html_to_pdf("<h1>Installed with Conan</h1>");
    if (pdf.size() < 4 || pdf.data() == nullptr) {
        return EXIT_FAILURE;
    }
    const auto prefix =
        std::string_view(reinterpret_cast<const char *>(pdf.data()), 4);
    return prefix == "%PDF" ? EXIT_SUCCESS : EXIT_FAILURE;
}
