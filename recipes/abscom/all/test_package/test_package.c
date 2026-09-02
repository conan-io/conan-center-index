#include <abscom/abs.h>
#include <stdio.h>

int main(void) {
    abs_init();
    var l = abs_new_list();
    append(l, abs_new_int(40));
    append(l, abs_new_int(2));
    var s = add(get(l, 0), get(l, 1));
    printf("sum=%.0f\n", abs_num_val(s));
    del(s);
    del(l);
    abs_cleanup();
    return 0;
}
