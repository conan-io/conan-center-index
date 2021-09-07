#include <wasmtime.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    char *wat = "(module\n"
                   "\t(func (param $lhs i32) (param $rhs i32) (result i32)\n"
                   "\t\tlocal.get $lhs\n"
                   "\t\tlocal.get $rhs\n"
                   "\t\ti32.add))";
    wasm_byte_vec_t ret;
    wasmtime_error_t *error = wasmtime_wat2wasm(wat, strlen(wat), &ret);
    printf("wasm:\n%s\n", wat);
    puts("assembly:");
    for(size_t i = 0; i < ret.size; ++i) {
        printf(" 0x%02x", ret.data[i]);
        if (i%8 == 7) {
            puts("");
        }
    }
    puts("");
    return EXIT_SUCCESS;
}
