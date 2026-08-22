#include <test_schema/test_schema.hpp>

#include <cstdlib>
#include <array>

int main(void)
{
    std::array<char, 64> buf{};
    auto msg = sbepp::make_view<test_schema::messages::msg1>(
        buf.data(), buf.size());
    return EXIT_SUCCESS;
}
