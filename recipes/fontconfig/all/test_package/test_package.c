#include <fontconfig/fontconfig.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

void print_config_files(FcStrList *files) {
  assert(files != NULL);

  FcChar8 *file;
  while ((file = FcStrListNext(files)) != NULL) {
    printf("Config file: %s\n", file);
  }
}

int main() {
  printf("Fontconfig version: %d\n", FcGetVersion());

  if (!FcInit()) {
    printf("FcInit() failed\n");
    return EXIT_FAILURE;
  }

  FcConfig *config = FcConfigGetCurrent();
  if (!config) {
    printf("FcConfigGetCurrent() failed: no config loaded\n");
    FcFini();
    return EXIT_FAILURE;
  }

  FcStrList *files = FcConfigGetConfigFiles(config);
  FcChar8 *file = FcStrListNext(files);
  if (!file) {
    printf("No config file loaded\n");
    FcStrListDone(files);
    FcFini();
    return EXIT_FAILURE;
  }
  print_config_files(files);
  FcStrListDone(files);

  FcFini();
  return EXIT_SUCCESS;
}
