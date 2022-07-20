#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <opencc/opencc.h>

int main(int argc, char** argv) {
  if (argc < 2) {
    fprintf(stderr, "Usage: %s CONFIGFILEPATH\n", argv[0]);
    return EXIT_FAILURE;
  }
  char* configFilePath = argv[1];
  opencc_t opencc = opencc_open(configFilePath);
  const char* input = "漢字";
  char* converted = opencc_convert_utf8(opencc, input, strlen(input));  // 汉字
  fprintf(stdout, "Tranditional: %s to Simplified: %s\n", input, converted);
  opencc_convert_utf8_free(converted);
  opencc_close(opencc);
  return EXIT_SUCCESS;
}
