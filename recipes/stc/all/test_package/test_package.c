#include "stc/cstr.h"

int main(void) {
    cstr str = cstr_lit("stc test package");
    isize pos = cstr_find_at(&str, 0, "test");
    printf("stc test package successful\n");
}
