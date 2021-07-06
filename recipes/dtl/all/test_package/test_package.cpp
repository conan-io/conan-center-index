#include <string>
#include <dtl/dtl.hpp>

int main()
{
    std::string a = "abc";
    std::string b = "abd";
    dtl::Diff<char, std::string> diff(a, b);
    diff.compose();
}
