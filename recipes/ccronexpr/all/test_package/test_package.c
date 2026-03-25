#include <stdio.h>
#include <time.h>
#include <ccronexpr.h>

int main(void) {
    cron_expr expr;
    const char* err;

    cron_parse_expr("* * * * * *", &expr, &err);
    cron_next(&expr, time(NULL));

    printf("Succeeded\n");
    return 0;
}
