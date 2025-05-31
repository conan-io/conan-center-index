#ifdef TRACY_GE_0_12
#include <tracy/tracy/Tracy.hpp>
#else
#include <tracy/Tracy.hpp>
#endif

int main(int argc, char **argv) {
  ZoneScopedN("main");

  return 0;
}
