#ifdef TRACY_GE_0_9
#include <tracy/Tracy.hpp>
#else
#include <Tracy.hpp>
#endif

int main(int argc, char **argv) {
  ZoneScopedN("main");

  return 0;
}
