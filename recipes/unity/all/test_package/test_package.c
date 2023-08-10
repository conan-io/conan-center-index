#include <unity.h>


void setUp(void)
{
}

void tearDown(void)
{
}

void test_Something(void)
{
    TEST_ASSERT_EQUAL_INT(1, 1);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_Something);
    return UNITY_END();
}
