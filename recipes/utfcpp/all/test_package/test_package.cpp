#include "utf8.h"
#include <iostream>
#include <string>
#include <cstdint>


using namespace std;

int main(int argc, char** argv)
{
    // U+1f600, grinning smiley face
    std::string text = "\xf0\x9f\x98\x80";
    bool valid = utf8::is_valid(text.begin(), text.end());
    std::ptrdiff_t length = utf8::distance(text.begin(), text.end());

    std::cout << "Valid = " << valid << " length = " << length << "\n";
    return 0;
}
