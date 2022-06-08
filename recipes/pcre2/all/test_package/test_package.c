#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>


int main() {
    pcre2_code *re;
    int rc;
    PCRE2_SIZE erroffset;
    int errcode;
    PCRE2_SIZE* ovector;
    const char *pattern = "\\w+";
    size_t pattern_size = strlen(pattern);
    const char *subject = "conan";
    size_t subject_size = strlen(subject);
    uint32_t options = 0;
    pcre2_match_data *match_data;
    uint32_t ovecsize = 128;

    re = pcre2_compile(pattern, pattern_size, options, &errcode, &erroffset, NULL);
    match_data = pcre2_match_data_create(ovecsize, NULL);
    rc = pcre2_match(re, subject, subject_size, 0, options, match_data, NULL);
    ovector = pcre2_get_ovector_pointer(match_data);
    PCRE2_SPTR start = subject + ovector[0];
    PCRE2_SIZE slen = ovector[1] - ovector[0];
    printf("match: %.*s\n", (int)slen, (char *)start );
    pcre2_match_data_free(match_data);
    pcre2_code_free(re);

    return EXIT_SUCCESS;
}
