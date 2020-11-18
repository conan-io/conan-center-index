#include <cstdlib>
#include <iostream>
#include "notcurses/notcurses.h"

int main() {
  // requires a valid TERM to be set, and the relevant terminfo entry installed
  auto nc = notcurses_init(NULL, NULL);
  if(nc == nullptr){
    return EXIT_FAILURE;
  }
  if(notcurses_stop(nc)){
    return EXIT_FAILURE;
  }
  return EXIT_SUCCESS;
}
