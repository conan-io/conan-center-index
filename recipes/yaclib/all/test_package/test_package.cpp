#include <cstdlib>

#include "yaclib/async/contract.hpp"
#include "yaclib/util/result.hpp"

int main()
{
    auto [f, p] = yaclib::MakeContract<int>();

    std::move(p).Set(42);

    if (!f.Ready())
    {
        return EXIT_FAILURE;
    }

    yaclib::Result<int> result = std::move(f).Get();

    if (std::move(result).Ok() != 42)
    {
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
