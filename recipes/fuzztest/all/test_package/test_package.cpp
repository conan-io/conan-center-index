// From
// https://github.com/google/fuzztest/blob/e317d5277e34948ae7048cb5e48309e0288e8df3/doc/quickstart-cmake.md#create-and-run-a-fuzz-test

#include "fuzztest/fuzztest.h"
#include "gtest/gtest.h"

TEST(MyTestSuite, OnePlustTwoIsTwoPlusOne) {
    EXPECT_EQ(1 + 2, 2 + 1);
}

void IntegerAdditionCommutes(int a, int b) {
    EXPECT_EQ(a + b, b + a);
}
FUZZ_TEST(MyTestSuite, IntegerAdditionCommutes);