#include <CppUTest/TestHarness.h>
#include <CppUTest/TestRegistry.h>
#include <CppUTest/CommandLineTestRunner.h>

TEST_GROUP(FirstTestGroup)
{
};

TEST(FirstTestGroup, FirstTest)
{
    CHECK_TRUE(true);
}

int main(int argc, const char** argv)
{
    CommandLineTestRunner runner(argc, argv, TestRegistry::getCurrentRegistry());
    return runner.runAllTestsMain();
}
