#include <fast_double_parser.h>
#include <string>

int main() {
    std::string a = "0.";
    double x;
    bool ok = fast_double_parser::parse_number(a.c_str(), &x);
    return 0;
}
