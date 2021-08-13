#include <Platform.Equality.h>
#include <gtest/gtest.h>

#include <span>
#include <list>

namespace Platform::Equality::Tests
{
    TEST(EqualityTest, BaseAnyEqual)
    {
        {
            int a = 0x228;
            int b = 0x1337;
            ASSERT_NE(std::any(a), std::any(b));
        }

        {
            int a = 0x177013;
            float b = 0x177013;
            ASSERT_NE(std::any(a), std::any(b));
        }

        {
            auto a = "i love green stuff";
            auto b = std::string{ "i love green stuff" };
            ASSERT_NE(std::any(a), std::any(b));
        }

        {
            auto a = "i love green stuff";
            auto b = "i love green stuff";
            ASSERT_EQ(std::any(a), std::any(b));
        }

        {
            auto a = std::string{ "i love green stuff" };
            auto b = std::string{ "i love green stuff" };
            ASSERT_EQ(std::any(a), std::any(b));
        }

        {
            std::vector<int> a{ 1, 2, 3, 4 };
            std::vector<int> b{ 1, 2, 3, 4 };
            EXPECT_ANY_THROW(std::any(a) == std::any(b));
            EXPECT_THROW(std::any(a) == std::any(b), std::runtime_error);
        }
    }

    TEST(EqualityTest, AdvancedAnyEqual)
    {
        {
            int a = 12;
            std::any b = a;
            ASSERT_EQ(a, b);
        }
        {
            ASSERT_EQ((std::any)1, (const std::any)1);
            ASSERT_EQ((std::any)1, (const std::any&)1);
            ASSERT_EQ((std::any)1, (std::any&&)1);
        }
    }

    TEST(EqualityTest, AggressiveAnyTest)
    {
        {
            int steps = 1e6;
            while (steps--)
            {
                int a = rand();
                int b = rand();

                if (a == b)
                {
                    ASSERT_EQ(std::any(a), std::any(b));
                }
                else
                {
                    ASSERT_NE(std::any(a), std::any(b));
                }
            }
        }
    }

    TEST(EqualityTest, RegisterTest)
    {
        {
            struct Nil { };
            RegisterEqualityComparer<Nil>([](auto a, auto b){ return true; });
            ASSERT_EQ(std::any(Nil{}), std::any(Nil{}));
        }

        {
            struct Nil { };
            RegisterEqualityComparer<Nil>([](auto a, auto b) { return false; });
            ASSERT_NE(std::any(Nil{}), std::any(Nil{}));
        }
    }

    TEST(EqualityTest, RangeEquality)
    {
        {
            std::vector<int> a{ 1, 2, 3, 4, 5 };
            std::vector<int> b{ 1, 2, 3, 4, 5 };
            auto left = std::span{ a };
            auto right = std::span{ b };
            ASSERT_EQ(a, b);
            ASSERT_TRUE(std::equal_to<std::span<int>>{}(left, right));
        }

        {
            std::vector<int> a{ 1, 2, 3, 4, 5 };
            std::vector<int> b{ 5, 4, 3, 2, 1 };
            auto left = std::span{ a };
            auto right = std::span{ b };
            ASSERT_NE(a, b);
            ASSERT_FALSE(std::equal_to<std::span<int>>{}(left, right));
        }
    }
}
