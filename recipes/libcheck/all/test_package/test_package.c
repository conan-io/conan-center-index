#include "check.h"

#include <stdio.h>

static int f(void) {
    return 5;
}

static const char *s(void) {
    return "EUR";
}


START_TEST (test_name)
{
    ck_assert_int_eq(f(), 5);
    ck_assert_str_eq(s(), "USD");
}
END_TEST

Suite *test_package_suite(void)
{
    Suite *s;
    TCase *tc_core;

    s = suite_create("test_package");

    tc_core = tcase_create("test_name");

    tcase_add_test(tc_core, test_name);
    suite_add_tcase(s, tc_core);

    return s;
}

int main(void) {
    Suite *s = test_package_suite();
    SRunner *sr = srunner_create(s);

    srunner_run_all(sr, CK_VERBOSE);
    int number_failed = srunner_ntests_failed(sr);
    srunner_free(sr);
    printf("number failed: %d\n", number_failed);
    printf("Ignore this intentional failure!\n");
    return 0;
}
