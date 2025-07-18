#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pact.h>

int main (int argc, char **argv) {
  pactffi_log_to_buffer(LevelFilter_Trace);

  VerifierHandle *handle = pactffi_verifier_new();
  pactffi_verifier_shutdown(handle);

  return 0;
}