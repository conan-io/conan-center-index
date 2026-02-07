#include <stdio.h>
#include <stdlib.h>

#include <ccronexpr.h>

int main(void) {
    cron_expr expr;
    const char* err = NULL;
    memset(&expr, 0, sizeof(expr));
    cron_parse_expr("0 */2 1-4 * * *", &expr, &err);
    if (err) {
        fprintf(stderr, "Error parsing cron expression: %s\n", err);
        return EXIT_FAILURE;
    }
    time_t cur = time(NULL);
    time_t next = cron_next(&expr, cur);

    struct tm* next_tm = localtime(&next);
    printf("Next occurrence: %02d:%02d:%02d\n", next_tm->tm_hour, next_tm->tm_min, next_tm->tm_sec);
    
    return EXIT_SUCCESS;
}
