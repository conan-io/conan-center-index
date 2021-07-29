#include "rtl-sdr.h"

#include <iostream>

int main() {
  std::cout << rtlsdr_get_ver_id();
  return 0;
}
