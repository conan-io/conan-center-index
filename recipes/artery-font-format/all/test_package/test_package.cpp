#include <cstdio>
#include <cstdlib>
#include <iostream>

#include <artery-font/std-artery-font.h>
#include <artery-font/stdio-serialization.h>

int main(int argc, char *argv[]) {
  if (argc < 2) {
      std::cerr << "usage: test_package <arfont file>\n";
      return EXIT_FAILURE;
  }

  FILE *const font_file = fopen(argv[1], "rb");
  if (font_file == nullptr) {
    std::cerr << "couldn't open font file" << std::endl;
    return EXIT_FAILURE;
  }

  artery_font::StdArteryFont<float> font;
  if (!artery_font::read(font, font_file)) {
    std::cerr << "couldn't read artery font" << std::endl;
    return EXIT_FAILURE;
  }

  if (fclose(font_file) != 0) {
    std::cerr << "an error occured when closing font file" << std::endl;
    return EXIT_FAILURE;
  }

  return EXIT_SUCCESS;
}
