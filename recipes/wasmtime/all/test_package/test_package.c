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
    if (error != NULL) {
        fprintf(stderr, "wasmtime_wat2wasm failed:\n");
        wasm_name_t message;
        wasmtime_error_message(error, &message);
        wasmtime_error_delete(error);
        fprintf(stderr, "%s\n", message.data);
        wasm_byte_vec_delete(&message);
        return EXIT_FAILURE;
    }
    printf("wasm text:\n%s\n", wat);
    puts("assembly:");
    for(size_t i = 0; i < ret.size; ++i) {
        printf(" 0x%02x", ret.data[i]);
        if (i%8 == 7) {
            puts("");
        }
    }
    puts("");
    wasm_byte_vec_delete(&ret);
    return EXIT_SUCCESS;
}
