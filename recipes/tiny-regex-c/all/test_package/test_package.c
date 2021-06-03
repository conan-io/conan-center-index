#include <re.h>

#include <stdio.h>

int main() {
    int match_length;
    const char *string_to_search = "ahem.. 'hello world !' ..";
    re_t pattern = re_compile("[Hh]ello [Ww]orld\\s*[!]?");

    int match_idx = re_matchp(pattern, string_to_search, &match_length);
    if (match_idx != -1) {
        printf("match at idx %i, %i chars long.\n", match_idx, match_length);
    }

    return 0;
}
