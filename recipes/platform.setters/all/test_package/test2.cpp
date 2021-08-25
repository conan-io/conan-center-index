#include <gtest/gtest.h>
#include <Platform.Setters.h>

namespace Platform::Setters::Tests
{
    TEST(SettersTests, ParameterlessConstructedSetterTest)
    {
        auto setter = Setter<std::int32_t>();
        ASSERT_EQ(0, setter.Result());
    }

    TEST(SettersTests, ConstructedWithDefaultValueSetterTest)
    {
        auto setter = Setter<std::int32_t>(9);
        ASSERT_EQ(9, setter.Result());
    }

    TEST(SettersTests, MethodsWithBooleanReturnTypeTest)
    {
        auto setter = Setter<std::int32_t>();
        ASSERT_TRUE(setter.SetAndReturnTrue(1));
        ASSERT_EQ(1, setter.Result());
        ASSERT_FALSE(setter.SetAndReturnFalse(2));
        ASSERT_EQ(2, setter.Result());
        auto array3 = std::to_array<std::int32_t>({3});
        ASSERT_TRUE(setter.SetFirstAndReturnTrue(array3));
        ASSERT_EQ(3, setter.Result());
        auto array4 = std::to_array<std::int32_t>({4});
        ASSERT_FALSE(setter.SetFirstAndReturnFalse(array4));
        ASSERT_EQ(4, setter.Result());
    }

    TEST(SettersTests, MethodsWithIntegerReturnTypeTest)
    {
        auto setter = Setter<std::int32_t, std::int32_t>(1, 0);
        ASSERT_EQ(1, setter.SetAndReturnTrue(1));
        ASSERT_EQ(1, setter.Result());
        ASSERT_EQ(0, setter.SetAndReturnFalse(2));
        ASSERT_EQ(2, setter.Result());
        auto array3 = std::to_array<std::int32_t>({3});
        ASSERT_EQ(1, setter.SetFirstAndReturnTrue(array3));
        ASSERT_EQ(3, setter.Result());
        auto array4 = std::to_array<std::int32_t>({4});
        ASSERT_EQ(0, setter.SetFirstAndReturnFalse(array4));
        ASSERT_EQ(4, setter.Result());
    }
}
