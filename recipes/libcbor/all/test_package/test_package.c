#include <cbor.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
  printf("Hello from libcbor %s\n", CBOR_VERSION);
#ifndef LIBCBOR_DEPRECATE_CUSTOM_ALLOC
  printf("Custom allocation support: %s\n", CBOR_CUSTOM_ALLOC ? "yes" : "no");
#endif
  printf("Pretty-printer support: %s\n", CBOR_PRETTY_PRINTER ? "yes" : "no");
  printf("Buffer growth factor: %f\n", (float)CBOR_BUFFER_GROWTH);
  cbor_item_t *array = cbor_new_definite_array(4);
  cbor_array_push(array, cbor_move(cbor_build_uint8(4)));
  cbor_array_push(array, cbor_move(cbor_build_uint8(3)));
  cbor_array_push(array, cbor_move(cbor_build_uint8(1)));
  cbor_array_push(array, cbor_move(cbor_build_uint8(2)));

  cbor_describe(array, stdout);
  fflush(stdout);
  /* Preallocate the map structure */
}
