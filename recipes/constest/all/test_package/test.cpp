#include <constest.hpp>
#include <gtest/gtest.h>

TEST(SimpleTest, ConstestedAssertion)
{
    CONSTEXPR_SECTION("Test constexpr section")
    {
        int value = 42;
        CONSTEXPR_EXPECT_EQ(value, 42);
    };
}

int main(int argc, char** argv)
{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
