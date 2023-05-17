#include <jpcre2.hpp>

typedef jpcre2::select<char> jp;

int main(int, char**)
{
    jp::Regex re;
    re.setPattern("Hello (\\S+?)").compile();
    if (!re.match("Hello conan-center-index"))
    {
        return 1;
    }

    return 0;
}
