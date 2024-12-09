#include <zeus/expected.hpp>

zeus::expected<void, int> func(int argc)
{
    if (argc > 1)
    {
        return {};
    }
    else
    {
        return zeus::unexpected(1);
    }
}

int main(int argc, char** argv)
{
    return func(argc)
        .and_then([] { return zeus::expected<int, int> {}; })
        .transform_error([](int) { return 0; })
        .error_or(1);
}
