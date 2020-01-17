#include "SpiceUsr.h"

#include <stdio.h>

int main () {
  ConstSpiceDouble rectan[3] = {0.0000, 1.0000, 1.0000};
  SpiceDouble radius;
  SpiceDouble longitude;
  SpiceDouble latitude;

  reclat_c(rectan, &radius, &longitude, &latitude);
  longitude *= dpr_c();
  latitude *= dpr_c();

  printf("Rectangular coordinates X=%f, Y=%f, Z=%f <=> Latitudinal coordinates r=%f, longitude=%f deg, latitude=%f deg\n",
         rectan[0], rectan[1], rectan[2], radius, longitude, latitude);

  return 0;
}
