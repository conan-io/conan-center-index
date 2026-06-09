#include <stdio.h>
#include <ft2build.h>
#include FT_FREETYPE_H

int main() {
  FT_Library library;
	int major, minor, patch;
	FT_Init_FreeType(&library);
	FT_Library_Version(library, &major, &minor, &patch);
  printf("Freetype library version: %d.%d.%d\n", major, minor, patch);
  FT_Done_FreeType(library);
  return 0;
}