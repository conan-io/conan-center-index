#include <sbepp/sbepp.hpp>

#include <cstdlib>

enum class Enum
{
    A,
    B
};

int main()
{
    auto underlying = sbepp::to_underlying(Enum::A);

    return EXIT_SUCCESS;
}
