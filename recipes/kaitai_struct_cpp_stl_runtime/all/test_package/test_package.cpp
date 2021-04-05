#include <kaitai/kaitaistream.h>

int main() {
    std::string buf;
    std::istringstream is(buf);
    kaitai::kstream ks(&is);
}
