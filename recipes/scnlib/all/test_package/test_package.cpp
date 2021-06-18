#include <scn/scn.h>

#include <string>

int main() {
    std::string s{"conan-center-index"};
    auto span = scn::make_span(s);
    return 0;
}
