#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <stlink.h>

int main(void) {
  stlink_t* sl;
  sl = stlink_open_usb(UERROR, CONNECT_NORMAL, NULL, 0);

  if (sl != NULL) {
    printf("-- version\n");
    stlink_version(sl);

    stlink_close(sl);
  }

  return EXIT_SUCCESS;
}
