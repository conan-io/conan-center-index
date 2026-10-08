#include <sys/types.h>
#include <time.h>
#include <stdint.h>

#include "munit.h"
#include "cclarify.h"

extern uint32_t __clar_format(
    struct clarifier* clar,
    enum __clar_loglevel loglevel,
    char* buf,
    const char* fmt,
    va_list* args,
    bool colors
    );

MunitResult clar_year_test(const MunitParameter params[], void* ptr) {
  char buf1[256], buf2[256];
  time_t tm;
  struct tm* tm_;

  tm = time(NULL);
  tm_ = localtime(&tm);

  clar_set_global_format("%Y");
  strftime(buf1, 255, "%Y", tm_);
  __clar_format(&__clar_default_fmt, CLAR_LOG_DEBUG, buf2, "", NULL, true);

  munit_assert_string_equal(buf1, buf2);

  return MUNIT_OK;
}

MunitResult clar_month_test(const MunitParameter params[], void* ptr) {
  char buf1[256], buf2[256];
  time_t tm;
  struct tm* tm_;

  tm = time(NULL);
  tm_ = localtime(&tm);

  clar_set_global_format("%M");
  strftime(buf1, 255, "%b", tm_);
  __clar_format(&__clar_default_fmt, CLAR_LOG_DEBUG, buf2, "", NULL, true);

  munit_assert_string_equal(buf1, buf2);

  return MUNIT_OK;
}

MunitResult clar_day_test(const MunitParameter params[], void* ptr) {
  char buf1[256], buf2[256];
  time_t tm;
  struct tm* tm_;

  tm = time(NULL);
  tm_ = localtime(&tm);

  clar_set_global_format("%d");
  strftime(buf1, 255, "%a", tm_);
  __clar_format(&__clar_default_fmt, CLAR_LOG_DEBUG, buf2, "", NULL, true);

  munit_assert_string_equal(buf1, buf2);

  return MUNIT_OK;
}

MunitResult clar_dof_test(const MunitParameter params[], void* ptr) {
  char buf1[256], buf2[256];
  time_t tm;
  struct tm* tm_;

  tm = time(NULL);
  tm_ = localtime(&tm);

  clar_set_global_format("%D");
  strftime(buf1, 255, "%d", tm_);
  __clar_format(&__clar_default_fmt, CLAR_LOG_DEBUG, buf2, "", NULL, true);

  munit_assert_string_equal(buf1, buf2);

  return MUNIT_OK;
}

MunitResult clar_hour_test(const MunitParameter params[], void* ptr) {
  char buf1[256], buf2[256];
  time_t tm;
  struct tm* tm_;

  tm = time(NULL);
  tm_ = localtime(&tm);

  clar_set_global_format("%H");
  strftime(buf1, 255, "%H", tm_);
  __clar_format(&__clar_default_fmt, CLAR_LOG_DEBUG, buf2, "", NULL, true);

  munit_assert_string_equal(buf1, buf2);

  return MUNIT_OK;
}

MunitResult clar_minute_test(const MunitParameter params[], void* ptr) {
  char buf1[256], buf2[256];
  time_t tm;
  struct tm* tm_;

  tm = time(NULL);
  tm_ = localtime(&tm);

  clar_set_global_format("%m");
  strftime(buf1, 255, "%M", tm_);
  __clar_format(&__clar_default_fmt, CLAR_LOG_DEBUG, buf2, "", NULL, true);

  munit_assert_string_equal(buf1, buf2);

  return MUNIT_OK;
}

MunitResult clar_second_test(const MunitParameter params[], void* ptr) {
  char buf1[256], buf2[256];
  time_t tm;
  struct tm* tm_;

  tm = time(NULL);
  tm_ = localtime(&tm);

  clar_set_global_format("%s");
  strftime(buf1, 255, "%S", tm_);
  __clar_format(&__clar_default_fmt, CLAR_LOG_DEBUG, buf2, "", NULL, true);

  munit_assert_string_equal(buf1, buf2);

  return MUNIT_OK;
}


MunitTest tests[] = {
  {
    "cclarify-year-test",
    clar_year_test,
    NULL,
    NULL,
    MUNIT_TEST_OPTION_NONE,
    NULL
  },
  {
    "cclarify-month-test",
    clar_month_test,
    NULL,
    NULL,
    MUNIT_TEST_OPTION_NONE,
    NULL
  },
  {
    "cclarify-day-test",
    clar_day_test,
    NULL,
    NULL,
    MUNIT_TEST_OPTION_NONE,
    NULL
  },
  {
    "cclarify-dof-test",
    clar_dof_test,
    NULL,
    NULL,
    MUNIT_TEST_OPTION_NONE,
    NULL
  },
  {
    "cclarify-hour-test",
    clar_hour_test,
    NULL,
    NULL,
    MUNIT_TEST_OPTION_NONE,
    NULL
  },
  {
    "cclarify-minute-test",
    clar_minute_test,
    NULL,
    NULL,
    MUNIT_TEST_OPTION_NONE,
    NULL
  },
  {
    "cclarify-second-test",
    clar_second_test,
    NULL,
    NULL,
    MUNIT_TEST_OPTION_NONE,
    NULL
  },
  {
    NULL,
    NULL,
    NULL,
    NULL,
    MUNIT_TEST_OPTION_NONE, NULL
  }
};

static const MunitSuite test_suite = {
  (char*)"",
  tests,
  NULL,
  128,
  MUNIT_SUITE_OPTION_NONE
};

int main(int argc, char** argv) {
  return munit_suite_main(&test_suite, (void*)"cclarify", argc, argv);
}
