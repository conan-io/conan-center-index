/* -*- indent-tabs-mode: nil -*-
 */
#if defined(__linux__) && !defined(_GNU_SOURCE)
#define _GNU_SOURCE
#endif
#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS
#endif
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#ifdef _WIN32
#include <windows.h>
#include <io.h>
#define mode_t int
#define ssize_t int
#define open _open
/* cast the third argument of _read to suppress warning C4267 */
#define read(fd, buf, count) _read((fd), (buf), (unsigned int)(count))
/* cast the second argument of fgets to suppress warning C4267 */
#define fgets(s, size, fp) fgets((s), (int)(size), (fp))
#define close _close
#else
#include <unistd.h>
#include <dlfcn.h>
#endif
#include <funchook.h>

#ifdef _WIN32
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif

#ifdef __GNUC__
#define NOINLINE __attribute__((noinline))
#endif
#ifdef _MSC_VER
#define NOINLINE __declspec(noinline)
#endif

#if defined(__APPLE__) && defined(__clang_major__) && __clang_major__ >= 11
#define SKIP_TESTS_CHANGING_EXE
#endif

typedef int (*int_func_t)(void);
typedef uint64_t (*uint64_func_t)(uint64_t);

DLLEXPORT int get_val_in_exe(void);
extern int get_val_in_dll(void);
extern int call_get_val_in_dll(void);
extern int jump_get_val_in_dll(void);
extern uint64_t arm64_test_adr(uint64_t);
extern uint64_t arm64_test_beq(uint64_t);
extern uint64_t arm64_test_bne(uint64_t);
extern uint64_t arm64_test_cbnz(uint64_t);
extern uint64_t arm64_test_cbz(uint64_t);
extern uint64_t arm64_test_ldr_w(uint64_t);
extern uint64_t arm64_test_ldr_x(uint64_t);
extern uint64_t arm64_test_ldrsw(uint64_t);
extern uint64_t arm64_test_ldr_s(uint64_t);
extern uint64_t arm64_test_ldr_d(uint64_t);
extern uint64_t arm64_test_ldr_q(uint64_t);
extern uint64_t arm64_test_prfm(uint64_t);
extern uint64_t arm64_test_tbnz(uint64_t);
extern uint64_t arm64_test_tbz(uint64_t);
extern int x86_test_call_get_pc_thunk_ax(void);
extern int x86_test_call_get_pc_thunk_bx(void);
extern int x86_test_call_get_pc_thunk_cx(void);
extern int x86_test_call_get_pc_thunk_dx(void);
extern int x86_test_call_get_pc_thunk_si(void);
extern int x86_test_call_get_pc_thunk_di(void);
extern int x86_test_call_get_pc_thunk_bp(void);
extern int x86_test_call_and_pop_eax(void);
extern int x86_test_call_and_pop_ebx(void);
extern int x86_test_call_and_pop_ecx(void);
extern int x86_test_call_and_pop_edx(void);
extern int x86_test_call_and_pop_esi(void);
extern int x86_test_call_and_pop_edi(void);
extern int x86_test_call_and_pop_ebp(void);
extern int x86_test_error_jump1(void);
extern int x86_test_error_jump2(void);

extern void set_val_in_dll(int val);

/* Reset the register for return values.
 *  %eax for x86.
 *  %rax for x86_64.
 */
NOINLINE int reset_register()
{
    return 0;
}

int int_val = 0xbaceba11;

static int test_cnt;
static int error_cnt;
static int hook_is_called;
static int_func_t orig_func;
static uint64_func_t uint64_orig_func;

int get_val_in_exe(void)
{
    return int_val;
}

static int hook_func(void)
{
    hook_is_called = 1;
    return orig_func();
}

static uint64_t uint64_hook_func(uint64_t arg)
{
    hook_is_called = 1;
    return uint64_orig_func(arg);
}

#define TEST_FUNCHOOK_INT(func, load_type) test_funchook_int(func, #func, load_type)

enum load_type {
   LOAD_TYPE_IN_EXE,
   LOAD_TYPE_IN_DLL,
   LOAD_TYPE_NO_LOAD,
};

static void *load_func(const char *module, const char *func)
{
    void *addr;
#ifdef _WIN32
    HMODULE hMod = GetModuleHandleA(module);
        
    if (hMod == NULL) {
        printf("ERROR: Could not open module %s.\n", module ? module : "(null)");
        exit(1);
    }
    addr = (void *)GetProcAddress(hMod, func);
#else
    void *handle = dlopen(module, RTLD_LAZY | RTLD_NOLOAD);
    if (handle == NULL) {
        printf("ERROR: Could not open file %s.\n", module ? module : "(null)");
        exit(1);
    }
    addr = dlsym(handle, func);
    dlclose(handle);
#endif
    if (addr == NULL) {
        printf("ERROR: Could not get function address of %s.\n", func);
        exit(1);
    }
    return addr;
}

void test_funchook_int(volatile int_func_t func, const char *func_name, enum load_type load_type)
{
    funchook_t *funchook = funchook_create();
    int result;
    int expected;
    int rv;
    int_func_t func_real = NULL;

    test_cnt++;
    printf("[%d] test_funchook_int: %s\n", test_cnt, func_name);

    switch (load_type) {
    case LOAD_TYPE_IN_EXE:
        func_real = (int_func_t)load_func(NULL, func_name);
        break;
    case LOAD_TYPE_IN_DLL:
#ifdef _MSC_VER
        func_real = (int_func_t)load_func("funchook_test_dll", func_name);
#else
        func_real = (int_func_t)load_func("libfunchook_test.so", func_name);
#endif
        break;
    case LOAD_TYPE_NO_LOAD:
        break;
    }

    expected = ++int_val;
    set_val_in_dll(int_val);
    reset_register();
    result = func();
    if (expected != result) {
        printf("ERROR: %s should return %d but %d before hooking.\n", func_name, expected, result);
        error_cnt++;
        return;
    }
    if (func_real != NULL) {
        reset_register();
        result = func_real();
        if (expected != result) {
            printf("ERROR: %s (real) should return %d but %d before hooking.\n", func_name, expected, result);
            error_cnt++;
            return;
        }
    }
    orig_func = func;
    rv = funchook_prepare(funchook, (void**)&orig_func, hook_func);
    if (rv != 0) {
        printf("ERROR: failed to prepare hook %s. (%s)\n", func_name, funchook_error_message(funchook));
        error_cnt++;
        return;
    }
    rv = funchook_install(funchook, 0);
    if (rv != 0) {
        printf("ERROR: failed to install hook %s. (%s)\n", func_name, funchook_error_message(funchook));
        error_cnt++;
        return;
    }

    hook_is_called = 0;
    expected = ++int_val;
    set_val_in_dll(int_val);
    reset_register();
    result = func();
    if (hook_is_called == 0) {
        printf("ERROR: hook_func is not called by %s.\n", func_name);
        error_cnt++;
        return;
    }
    if (expected != result) {
        printf("ERROR: %s should return %d but %d after hooking.\n", func_name, expected, result);
        error_cnt++;
        return;
    }
    if (func_real != NULL) {
        hook_is_called = 0;
        reset_register();
        result = func_real();
        if (hook_is_called == 0) {
            printf("ERROR: hook_func is not called by %s (real).\n", func_name);
            error_cnt++;
            return;
        }
        if (expected != result) {
            printf("ERROR: %s (real) should return %d but %d after hooking.\n", func_name, expected, result);
            error_cnt++;
            return;
        }
    }

    funchook_uninstall(funchook, 0);

    expected = ++int_val;
    set_val_in_dll(int_val);
    reset_register();
    result = func();
    if (expected != result) {
        printf("ERROR: %s should return %d but %d after hook is removed.\n", func_name, expected, result);
        error_cnt++;
        return;
    }
    if (func_real != NULL) {
        reset_register();
        result = func_real();
        if (expected != result) {
            printf("ERROR: %s (real) should return %d but %d after hook is removed.\n", func_name, expected, result);
            error_cnt++;
            return;
        }
    }

    funchook_destroy(funchook);
}

#define TEST_FUNCHOOK_UINT64(func) test_funchook_uint64(func, #func)
void test_funchook_uint64(volatile uint64_func_t func, const char *func_name)
{
    funchook_t *funchook = funchook_create();
    uint64_t test_data[] = {0, 0xFFFFFFFFFFFFFFFF, 0x8000000000000000, 0x2};
    uint64_t results[sizeof(test_data)/sizeof(test_data[0])];
    uint64_t result;
    size_t i, num_test_data = sizeof(test_data)/sizeof(test_data[0]);
    int rv;

    test_cnt++;
    printf("[%d] test_funchook_uint64: %s\n", test_cnt, func_name);

    for (i = 0; i < num_test_data; i++) {
        results[i] = func(test_data[i]);
        //fprintf(stderr, "%s(0x%"PRIx64") -> 0x%"PRIx64"\n", func_name, test_data[i], results[i]);
    }

    uint64_orig_func = func;
    rv = funchook_prepare(funchook, (void**)&uint64_orig_func, uint64_hook_func);
    if (rv != 0) {
        printf("ERROR: failed to prepare hook %s. (%s)\n", func_name, funchook_error_message(funchook));
        error_cnt++;
        return;
    }
    rv = funchook_install(funchook, 0);
    if (rv != 0) {
        printf("ERROR: failed to install hook %s. (%s)\n", func_name, funchook_error_message(funchook));
        error_cnt++;
        return;
    }

    for (i = 0; i < num_test_data; i++) {
        hook_is_called = 0;
        reset_register();
        result = func(test_data[i]);
        if (hook_is_called == 0) {
            printf("ERROR: hook_func is not called by %s.\n", func_name);
            error_cnt++;
            return;
        }
        if (results[i] != result) {
            printf("ERROR: %s should return 0x%"PRIx64" but 0x%"PRIx64" after hooking.\n", func_name, results[i], result);
            error_cnt++;
            return;
        }
    }

    funchook_uninstall(funchook, 0);

    for (i = 0; i < num_test_data; i++) {
        hook_is_called = 0;
        reset_register();
        result = func(test_data[i]);
        if (hook_is_called != 0) {
            printf("ERROR: hook_func is called after uninstall by %s.\n", func_name);
            error_cnt++;
            return;
        }
        if (results[i] != result) {
            printf("ERROR: %s should return 0x%"PRIx64" but 0x%"PRIx64" after uninstall.\n", func_name, results[i], result);
            error_cnt++;
            return;
        }
    }
}

#define TEST_FUNCHOOK_EXPECT_ERROR(func, errcode) test_funchook_expect_error(func, errcode, #func, __LINE__)
void test_funchook_expect_error(int_func_t func, int errcode, const char *func_str, int line)
{
    funchook_t *funchook = funchook_create();
    int rv;

    test_cnt++;
    printf("[%d] test_funchook_expect_error: %s\n", test_cnt, func_str);

    orig_func = func;
    rv = funchook_prepare(funchook, (void**)&orig_func, hook_func);
    if (rv != errcode) {
        printf("ERROR at line %d: hooking must fail with %d but %d.\n", line, errcode, rv);
        error_cnt++;
    }
    funchook_destroy(funchook);
}

#ifdef __ANDROID__
static int (*open_func)(const char* const pass_object_size, int, ...);
#else
static int (*open_func)(const char *pathname, int flags, mode_t mode);
#endif
static FILE *(*fopen_func)(const char *pathname, const char *mode);

static int open_hook(const char *pathname, int flags, mode_t mode)
{
    if (strcmp(pathname, "test-1.txt") == 0) {
        pathname = "test-2.txt";
    }
    return open_func(pathname, flags, mode);
}

static FILE *fopen_hook(const char *pathname, const char *mode)
{
    if (strcmp(pathname, "test-1.txt") == 0) {
        pathname = "test-2.txt";
    }
    return fopen_func(pathname, mode);
}

static void read_content_by_open(const char *filename, char *buf, size_t bufsiz)
{
    int fd = open(filename, O_RDONLY);
    ssize_t size = read(fd, buf, bufsiz);

    if (size >= 0) {
        buf[size] = '\0';
    } else {
        strcpy(buf, "read error");
    }
    close(fd);
}

static void read_content_by_fopen(const char *filename, char *buf, size_t bufsiz)
{
    FILE *fp = fopen(filename, "r");
    if (fp != NULL) {
        if (fgets(buf, bufsiz, fp) == NULL) {
            strcpy(buf, "read error");
        }
        fclose(fp);
    } else {
        strcpy(buf, "open error");
    }
}

static void check_content(const char *filename, const char *expect, int line)
{
    char buf[512];

    read_content_by_open(filename, buf, sizeof(buf));
    if (strcmp(buf, expect) != 0) {
        printf("ERROR at line %d: '%s' != '%s' (open)\n", line, buf, expect);
        error_cnt++;
    }
    read_content_by_fopen(filename, buf, sizeof(buf));
    if (strcmp(buf, expect) != 0) {
        printf("ERROR at line %d: '%s' != '%s' (fopen)\n", line, buf, expect);
        error_cnt++;
    }
}

static void test_hook_open_and_fopen(void)
{
    FILE *fp;
    funchook_t *funchook;
    int rv;

#ifdef WIN64
    if (getenv("WINELOADERNOEXEC") != NULL) {
        /* The test doesn't work on Wine. */
        return;
    }
#endif

    test_cnt++;
    printf("[%d] test_hook_open_and_fopen\n", test_cnt);

    /* prepare file contents */
    fp = fopen("test-1.txt", "w");
    fputs("This is test-1.txt.", fp);
    fclose(fp);
    fp = fopen("test-2.txt", "w");
    fputs("This is test-2.txt.", fp);
    fclose(fp);

    /* prepare to hook `open' and `fopen` */
    funchook = funchook_create();
#ifdef __ANDROID__
    open_func = (int (*)(const char* const pass_object_size, int, ...))open;
#else
    open_func = (int (*)(const char*, int, mode_t))open;
#endif
    funchook_prepare(funchook, (void**)&open_func, open_hook);
    fopen_func = fopen;
    funchook_prepare(funchook, (void**)&fopen_func, fopen_hook);

    /* The contents of test-1.txt should be "This is test-1.txt". */
    check_content("test-1.txt", "This is test-1.txt.", __LINE__);

    /* hook `open' and `fopen` */
    rv = funchook_install(funchook, 0);
    if (rv != 0) {
        printf("ERROR: failed to install open and fopen hooks. (%s)\n", funchook_error_message(funchook));
        error_cnt++;
        return;
    }
    /* Try to open test-1.txt but open test-2.txt. */
    check_content("test-1.txt", "This is test-2.txt.", __LINE__);

    /* restore hooks.  */
    funchook_uninstall(funchook, 0);
    /* Open test-1.txt. */
    check_content("test-1.txt", "This is test-1.txt.", __LINE__);

    funchook_destroy(funchook);
}

#define S(suffix) \
    extern int dllfunc_##suffix(int, int); \
    static int (*dllfunc_##suffix##_func)(int, int); \
    static int dllfunc_##suffix##_hook(int a, int b) { \
        return dllfunc_##suffix##_func(a, b) * 2; \
    } \
    NOINLINE int exefunc_##suffix(int a, int b) { return a * b + suffix; } \
    static int (*exefunc_##suffix##_func)(int, int); \
    static int exefunc_##suffix##_hook(int a, int b) { \
        return exefunc_##suffix##_func(a, b) * 2; \
    }
#include "suffix.list"
#undef S

static NOINLINE int call_many_funcs(int installed)
{
    int rv;
    int expected;
    int mul = installed ? 2 : 1;
    const char *is_str = installed ? "isn't" : "is";
#define S(suffix) \
    rv = dllfunc_##suffix(2, 3); \
    expected = (2 * 3 + suffix) * mul; \
    if (rv != expected) { \
        printf("ERROR: dllfunc_%s %s hooked. (expect %d but %d)\n", #suffix, is_str, expected, rv); \
        error_cnt++; \
        return -1; \
    }
#include "suffix.list"
#undef S
#ifndef SKIP_TESTS_CHANGING_EXE
#define S(suffix) \
    rv = exefunc_##suffix(2, 3); \
    expected = (2 * 3 + suffix) * mul; \
    if (rv != expected) { \
        printf("ERROR: exefunc_%s %s hooked. (expect %d but %d)\n", #suffix, is_str, expected, rv); \
        error_cnt++; \
        return -1; \
    }
#include "suffix.list"
#undef S
#endif
    return 0;
}

static void test_hook_many_funcs(void)
{
    funchook_t *funchook;
    int rv;

    test_cnt++;
    printf("[%d] test_hook_many_funcs\n", test_cnt);
    funchook = funchook_create();
#define S(suffix) \
    dllfunc_##suffix##_func = dllfunc_##suffix; \
    funchook_prepare(funchook, (void**)&dllfunc_##suffix##_func, dllfunc_##suffix##_hook); \
    putchar('.'); fflush(stdout); \
    funchook_set_debug_file(NULL); /* disable logging except the first to reduce log size. */
#include "suffix.list"
    funchook_set_debug_file("debug.log");
#undef S
#ifndef SKIP_TESTS_CHANGING_EXE
#define S(suffix) \
    exefunc_##suffix##_func = exefunc_##suffix; \
    funchook_prepare(funchook, (void**)&exefunc_##suffix##_func, exefunc_##suffix##_hook); \
    funchook_set_debug_file(NULL); /* disable logging except the first to reduce log size. */
#include "suffix.list"
    funchook_set_debug_file("debug.log");
#undef S
#endif
    putchar('\n');

    rv = funchook_install(funchook, 0);
    if (rv != 0) {
        printf("ERROR: failed to install hooks. (%s)\n", funchook_error_message(funchook));
        error_cnt++;
        return;
    }
    if (call_many_funcs(1) != 0) {
        return;
    }

    funchook_uninstall(funchook, 0);
    if (call_many_funcs(0) != 0) {
        return;
    }

    funchook_destroy(funchook);
}

int main()
{
    funchook_set_debug_file("debug.log");

#ifdef SKIP_TESTS_CHANGING_EXE
    printf("*** Skip tests changing executable compiled by Xcode 11.0 or upper on macOS. ***\n");
#else
    TEST_FUNCHOOK_INT(get_val_in_exe, LOAD_TYPE_IN_EXE);
#endif
    TEST_FUNCHOOK_INT(get_val_in_dll, LOAD_TYPE_IN_DLL);
    TEST_FUNCHOOK_INT(call_get_val_in_dll, LOAD_TYPE_IN_DLL);
    TEST_FUNCHOOK_INT(jump_get_val_in_dll, LOAD_TYPE_IN_DLL);

#ifdef __aarch64__
    TEST_FUNCHOOK_UINT64(arm64_test_adr);
    TEST_FUNCHOOK_UINT64(arm64_test_beq);
    TEST_FUNCHOOK_UINT64(arm64_test_bne);
    TEST_FUNCHOOK_UINT64(arm64_test_cbnz);
    TEST_FUNCHOOK_UINT64(arm64_test_cbz);
    TEST_FUNCHOOK_UINT64(arm64_test_ldr_w);
    TEST_FUNCHOOK_UINT64(arm64_test_ldr_x);
    TEST_FUNCHOOK_UINT64(arm64_test_ldrsw);
    TEST_FUNCHOOK_UINT64(arm64_test_ldr_s);
    TEST_FUNCHOOK_UINT64(arm64_test_ldr_d);
    TEST_FUNCHOOK_UINT64(arm64_test_ldr_q);
    TEST_FUNCHOOK_UINT64(arm64_test_prfm);
    TEST_FUNCHOOK_UINT64(arm64_test_tbnz);
    TEST_FUNCHOOK_UINT64(arm64_test_tbz);
#endif

#ifndef _MSC_VER
#if defined __i386 || defined  _M_I386
    TEST_FUNCHOOK_EXPECT_ERROR(x86_test_error_jump1, FUNCHOOK_ERROR_CANNOT_FIX_IP_RELATIVE);
    TEST_FUNCHOOK_EXPECT_ERROR(x86_test_error_jump2, FUNCHOOK_ERROR_FOUND_BACK_JUMP);

#ifndef _WIN32
    TEST_FUNCHOOK_INT(x86_test_call_get_pc_thunk_ax, LOAD_TYPE_NO_LOAD);
    TEST_FUNCHOOK_INT(x86_test_call_get_pc_thunk_bx, LOAD_TYPE_NO_LOAD);
    TEST_FUNCHOOK_INT(x86_test_call_get_pc_thunk_cx, LOAD_TYPE_NO_LOAD);
    TEST_FUNCHOOK_INT(x86_test_call_get_pc_thunk_dx, LOAD_TYPE_NO_LOAD);
    TEST_FUNCHOOK_INT(x86_test_call_get_pc_thunk_si, LOAD_TYPE_NO_LOAD);
    TEST_FUNCHOOK_INT(x86_test_call_get_pc_thunk_di, LOAD_TYPE_NO_LOAD);
    TEST_FUNCHOOK_INT(x86_test_call_get_pc_thunk_bp, LOAD_TYPE_NO_LOAD);
    TEST_FUNCHOOK_INT(x86_test_call_and_pop_eax, LOAD_TYPE_NO_LOAD);
    TEST_FUNCHOOK_INT(x86_test_call_and_pop_ebx, LOAD_TYPE_NO_LOAD);
    TEST_FUNCHOOK_INT(x86_test_call_and_pop_ecx, LOAD_TYPE_NO_LOAD);
    TEST_FUNCHOOK_INT(x86_test_call_and_pop_edx, LOAD_TYPE_NO_LOAD);
    TEST_FUNCHOOK_INT(x86_test_call_and_pop_esi, LOAD_TYPE_NO_LOAD);
    TEST_FUNCHOOK_INT(x86_test_call_and_pop_edi, LOAD_TYPE_NO_LOAD);
    TEST_FUNCHOOK_INT(x86_test_call_and_pop_ebp, LOAD_TYPE_NO_LOAD);
#endif
#endif

#endif

    test_hook_open_and_fopen();
    test_hook_many_funcs();

    if (error_cnt == 0) {
        printf("all %d tests are passed.\n", test_cnt);
        return 0;
    } else {
        printf("%d of %d tests are failed.\n", error_cnt, test_cnt);
        return 1;
    }
}
