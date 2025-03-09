#include <gtest/gtest.h>
#include <stdx/utils.hpp>
#include <stdx/flag.hpp>
#include <cstdint>

// Example enum for testing
enum class MyFlags : std::uint8_t
{
    None  = 0x00,
    Flag1 = 0x01,
    Flag2 = 0x02,
    Flag3 = 0x04,
    All   = Flag1 | Flag2 | Flag3
};

using namespace stdx::utils;
using stdx::Flag;

// Tests for utils.hpp
TEST(UtilsTests, IsValidCombination)
{
    EXPECT_TRUE(is_valid_combination<MyFlags>(0));
    EXPECT_TRUE(is_valid_combination<MyFlags>(1)); // Flag1
    EXPECT_TRUE(is_valid_combination<MyFlags>(2)); // Flag2
    EXPECT_TRUE(is_valid_combination<MyFlags>(4)); // Flag3
    EXPECT_TRUE(is_valid_combination<MyFlags>(3)); // Flag1 | Flag2
    EXPECT_TRUE(is_valid_combination<MyFlags>(5)); // Flag1 | Flag3
    EXPECT_TRUE(is_valid_combination<MyFlags>(6)); // Flag2 | Flag3
    EXPECT_TRUE(is_valid_combination<MyFlags>(7)); // Flag1 | Flag2 | Flag3
    EXPECT_FALSE(is_valid_combination<MyFlags>(8)); // Out-of-range bit
}

TEST(UtilsTests, CombineFlags)
{
    auto combined1 = combine_flags(MyFlags::Flag1);
    EXPECT_EQ(combined1, static_cast<std::uint8_t>(0x01));

    auto combined2 = combine_flags(MyFlags::Flag1, MyFlags::Flag2);
    EXPECT_EQ(combined2, static_cast<std::uint8_t>(0x01 | 0x02));

    auto combined3 = combine_flags(MyFlags::Flag1, MyFlags::Flag2, MyFlags::Flag3);
    EXPECT_EQ(combined3, static_cast<std::uint8_t>(0x01 | 0x02 | 0x04));
}

// Tests for Flag class
TEST(FlagTests, DefaultConstructor)
{
    Flag<MyFlags> f_default;
    EXPECT_EQ(f_default.get(), static_cast<std::uint8_t>(0));
}

TEST(FlagTests, ConstructorSingleEnumValue)
{
    Flag<MyFlags> f_single(MyFlags::Flag1);
    EXPECT_EQ(f_single.get(), static_cast<std::uint8_t>(0x01));
}

TEST(FlagTests, VariadicConstructor)
{
    Flag<MyFlags> f_variadic(MyFlags::Flag1, MyFlags::Flag2, MyFlags::Flag3);
    EXPECT_EQ(f_variadic.get(), static_cast<std::uint8_t>(0x01 | 0x02 | 0x04));
}

TEST(FlagTests, ConstructorFromNumericTypeValid)
{
    Flag<MyFlags> f_num_valid(3); // 3 == Flag1 | Flag2
    EXPECT_EQ(f_num_valid.get(), static_cast<std::uint8_t>(3));
}

TEST(FlagTests, ConstructorFromNumericTypeInvalid)
{
    EXPECT_THROW({
        Flag<MyFlags> f_num_invalid(8); // 8 is invalid for MyFlags
    }, std::invalid_argument);
}

TEST(FlagTests, AddFlags)
{
    Flag<MyFlags> f_add(MyFlags::Flag1);
    f_add.add(MyFlags::Flag2, MyFlags::Flag3);
    EXPECT_EQ(f_add.get(), static_cast<std::uint8_t>(0x01 | 0x02 | 0x04));
}

TEST(FlagTests, RemoveFlags)
{
    Flag<MyFlags> f_remove(MyFlags::Flag1, MyFlags::Flag2, MyFlags::Flag3);
    f_remove.remove(MyFlags::Flag2);
    EXPECT_EQ(f_remove.get(), static_cast<std::uint8_t>(0x01 | 0x04));
}

TEST(FlagTests, HasFlags)
{
    Flag<MyFlags> f_has(MyFlags::Flag1, MyFlags::Flag2);
    EXPECT_TRUE(f_has.has(MyFlags::Flag1));
    EXPECT_TRUE(f_has.has(MyFlags::Flag2));
    EXPECT_TRUE(f_has.has(MyFlags::Flag1, MyFlags::Flag2));
    EXPECT_FALSE(f_has.has(MyFlags::Flag3));
}

TEST(FlagTests, BitwiseOperators)
{
    // Operator|
    Flag<MyFlags> f_or_1(MyFlags::Flag1);
    auto f_or_2 = f_or_1 | MyFlags::Flag2;
    EXPECT_EQ(f_or_2.get(), static_cast<std::uint8_t>(0x01 | 0x02));

    // Operator|=
    Flag<MyFlags> f_or_assign(MyFlags::Flag1);
    f_or_assign |= MyFlags::Flag3;
    EXPECT_EQ(f_or_assign.get(), static_cast<std::uint8_t>(0x01 | 0x04));

    // Operator&
    Flag<MyFlags> f_and(MyFlags::Flag1, MyFlags::Flag2, MyFlags::Flag3); // 7
    auto f_and_result = f_and & MyFlags::Flag2;
    EXPECT_EQ(f_and_result.get(), static_cast<std::uint8_t>(0x02));

    // Operator&=
    Flag<MyFlags> f_and_assign(MyFlags::Flag1, MyFlags::Flag2); // 3
    f_and_assign &= MyFlags::Flag1;
    EXPECT_EQ(f_and_assign.get(), static_cast<std::uint8_t>(0x01));

    // Operator~
    Flag<MyFlags> f_not(MyFlags::Flag1);
    auto f_not_result = ~f_not;
    EXPECT_NE(f_not_result.get(), static_cast<std::uint8_t>(0x01));
}

TEST(FlagTests, EqualityOperators)
{
    Flag<MyFlags> f_eq_1(MyFlags::Flag1, MyFlags::Flag2); // 3
    Flag<MyFlags> f_eq_2(MyFlags::Flag1, MyFlags::Flag2); // 3
    Flag<MyFlags> f_neq(MyFlags::Flag3);                  // 4

    EXPECT_TRUE(f_eq_1 == f_eq_2);
    EXPECT_TRUE(f_eq_1 != f_neq);
}

// Main entry point for Google Test
int main(int argc, char** argv)
{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
