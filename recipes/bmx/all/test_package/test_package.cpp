#include <bmx/Version.h>
#include <mxf/mxf_version.h>

#include <iostream>

int main() {
    std::cout << bmx::get_bmx_library_name() << " library version " << bmx::get_bmx_version_string() << std::endl;

    const auto mxf_version = mxf_get_version();
    std::cout << "MXF library version "
              << mxf_version->major << '.' << mxf_version->minor << '.' << mxf_version->patch << std::endl;

    return 0;
}
