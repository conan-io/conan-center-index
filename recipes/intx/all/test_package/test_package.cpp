#include <intx/intx.hpp>

int main(int argc, char**)
{
    return static_cast<int>(intx::uint512{argc} / (intx::uint512{1} << 111));
}
