#include "zoe/zoe.h"

int main(int argc, char** argv) {
  using namespace zoe;

  Zoe::GlobalInit();

  Zoe efd;

  Zoe::GlobalUnInit();

  return 0;
}
