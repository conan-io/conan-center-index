#include <rapidfuzz/fuzz.hpp>
#include <string>

int main() {
    std::string s1("new york mets");
    std::string s2("new YORK mets");
    int r = rapidfuzz::fuzz::ratio(s1, s1);
    if (r == 100) {
        return 0;
    } else {
        return -1;
    }
}
