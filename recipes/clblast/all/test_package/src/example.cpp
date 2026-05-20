#include <cstdio>
#include <clblast.h>

int main() {
  auto success = clblast::StatusCode::kSuccess;
  bool ok = static_cast<int>(success) == 0;
  printf("CLBlast API check: %s\n", ok ? "PASS" : "FAIL");
  return ok ? 0 : 1;
}
