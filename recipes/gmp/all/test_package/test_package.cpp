#include <cstdlib>
#include <gmp.h>


int main (void) {

  mpz_t a,b,c;
  mpz_inits(a,b,c,NULL);

  mpz_set_str(a, "1234", 10);
  return EXIT_SUCCESS;
}
