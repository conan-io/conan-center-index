#if defined(_MSC_VER)
#pragma runtime_checks("s", off)
#endif

#include <ffi.h>

#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

unsigned print_uint(unsigned arg) {
    printf("print_int(%u)\n", arg);
    return 3 * arg;
}

typedef struct {
    FILE *stream;
} puts_binding_userdata;

void puts_binding(ffi_cif *cif, void *ret, void** args, void *userdata)
{
    fputs(*(char **)args[0], ((puts_binding_userdata *)userdata)->stream);
    *((unsigned*)ret) = 1337;
}

int main()
{
    {
	    ffi_type *argtypes[1] = {&ffi_type_uint32};
        ffi_cif cif;
        ffi_status status = FFI_BAD_ABI;
        status = ffi_prep_cif(&cif, FFI_DEFAULT_ABI, 1, &ffi_type_uint32, argtypes);
        if (status != FFI_OK)
        {
            puts("1 ffi_prep_cif FAILED.\n\n");
            return EXIT_FAILURE;
        }
        #ifndef DISABLE_FFI_CALL
        // this fails on msvc debug runtime because of https://github.com/libffi/libffi/issues/456
        unsigned rvalue = 0;
        unsigned arg1 = 13;
        const unsigned expected_ret = 3 * arg1;
        void *args[] = {(void*)(&arg1)};
        ffi_call(&cif, FFI_FN(&print_uint), (void *) &rvalue, args);
        printf("ffi_call returns %d (should be %d)\n", rvalue, expected_ret);
        if (rvalue != expected_ret) {
            printf("ffi_call FAILED. Expected %d, but got %d.\n", expected_ret, rvalue);
            return EXIT_FAILURE;
        }
        #endif
        return EXIT_SUCCESS;
    }
    {
        #ifdef FFI_CLOSURES
	    ffi_type *argtypes[1] = {&ffi_type_uint};
        ffi_cif cif;
        ffi_status status = FFI_BAD_ABI;
        status = ffi_prep_cif(&cif, FFI_DEFAULT_ABI, 1, &ffi_type_uint32, argtypes);
        if (status != FFI_OK)
        {
            puts("2 ffi_prep_cif FAILED.\n\n");
            return EXIT_FAILURE;
        }
        unsigned (*bound_puts)(const char *) = NULL;
        ffi_closure *closure = NULL;
        closure = (ffi_closure *) ffi_closure_alloc(sizeof(ffi_closure), (void **)&bound_puts);
        if (closure == NULL) {
            puts("ffi_closure_alloc FAILED\n");
            return EXIT_FAILURE;
        }

        puts_binding_userdata userdata;
        userdata.stream = stdout;
        status = ffi_prep_closure_loc(closure, &cif, puts_binding,
                                      &userdata, (void *) bound_puts);
        if (status != FFI_OK) {
            puts("ffi_prep_closure_loc FAILED\n");
            return EXIT_FAILURE;
        }
        puts("Start calling bound_put():");
        bound_puts("Hello");
        bound_puts(" ");
        bound_puts("World");
        unsigned rc = bound_puts("\n");
        printf("bounds_puts returned %d.\n", rc);
        if (rc != 1337) {
            puts("bounds_put returned wrong number.");
            return EXIT_FAILURE;
        }

        ffi_closure_free(closure);
        #endif
    }
	return EXIT_SUCCESS;
}

#if defined(_MSC_VER)
#pragma runtime_checks("s", restore)
#endif
