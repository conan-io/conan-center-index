#include <pidwg/reader.hpp>

#include <cstdlib>


int main() {
    const pidwg::Document document;
    return pidwg::to_json(document).empty() ? EXIT_FAILURE : EXIT_SUCCESS;
}
