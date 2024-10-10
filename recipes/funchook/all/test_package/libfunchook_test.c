#ifdef _WIN32
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif

static int val_in_dll;

DLLEXPORT void set_val_in_dll(int val)
{
    val_in_dll = val;
}

DLLEXPORT int get_val_in_dll()
{
    return val_in_dll;
}

#define S(suffix) DLLEXPORT int dllfunc_##suffix(int a, int b) { return a * b + suffix; }
#include "suffix.list"
#undef S
