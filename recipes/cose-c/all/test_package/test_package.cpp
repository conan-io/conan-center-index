#include <cose.h>
#include <stdio.h>

int main(int argc, char *argv[]) {

  const int aCoseInitFlags = COSE_INIT_FLAGS_NONE;

  const auto mSign =
      COSE_Sign0_Init(static_cast<COSE_INIT_FLAGS>(aCoseInitFlags), nullptr);

  return 0;
}