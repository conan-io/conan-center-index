#include <cstdlib>
#include <iostream>

#include "capypdf.hpp"
#include "capypdf.h"

int main() {
    CapyPDF_DocumentProperties *opt{};
    auto rc = capy_document_properties_new(&opt);
    capy_document_properties_destroy(opt);
    std::cout << "CapyPDF version: " << CAPYPDF_VERSION_STR << std::endl;
    return EXIT_SUCCESS;
}
