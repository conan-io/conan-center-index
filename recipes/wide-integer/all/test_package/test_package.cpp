#include <math/wide_integer/uintwide_t.h>

int main(void) {
  using math::wide_integer::uint256_t;

  uint256_t a("0xF4DF741DE58BCB2F37F18372026EF9CBCFC456CB80AF54D53BDEED78410065DE");
  uint256_t b("0x166D63E0202B3D90ECCEAA046341AB504658F55B974A7FD63733ECF89DD0DF75");

  uint256_t c = (a * b);
  uint256_t d = (a / b);

  return 0;
}
