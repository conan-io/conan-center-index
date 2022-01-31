#include <stdio.h>
#include <funchook.h>

#ifdef __GNUC__
#define NOINLINE __attribute__((noinline))
#endif
#ifdef _MSC_VER
#define NOINLINE __declspec(noinline)
#endif

void target();
int installHook();
void hook();
int main();

int hook_invoked = 0;
void (*original_target)() = target;

NOINLINE void target() {
  printf("Target invoked\n");
}

int installHook() {
  funchook_t *funchook = funchook_create();
  int rv;

  rv = funchook_prepare(funchook, (void **)&original_target, hook);
  if (rv != 0) {
    return 1;
  }

  rv = funchook_install(funchook, 0);
  if (rv != 0) {
    return 1;
  }

  return 0;
}

void hook() {
  printf("Hook invoked\n");
  hook_invoked=1;
  original_target();
}

int main() {
  funchook_set_debug_file("funchook_debug.txt");

  if (installHook() == 1) {
    printf("Failed to install hook\n");
    return 1;
  }

  printf("Hook installed, invoking...\n");

  target();

  if (hook_invoked == 1) {
    printf("Test passed!\n");
    return 0;
  } else {
    printf("Test failed...hook was not invoked...\n");
    return 1;
  }
}
