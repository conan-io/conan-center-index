#include <iostream>

#include "capypdf.hpp"
#include "capypdf.h"

int main()
{
    CapyPDF_DocumentProperties *opt{};

    if (auto rc = capy_document_properties_new(&opt)) {
        std::cerr << capy_error_message(rc) << '\n';
        return 1;
    }

    if (auto rc = capy_document_properties_destroy(opt)) {
        std::cerr << capy_error_message(rc) << '\n';
        return 1;
    }

    std::cout << CAPYPDF_VERSION_STR << '\n';
    return 0;
}
