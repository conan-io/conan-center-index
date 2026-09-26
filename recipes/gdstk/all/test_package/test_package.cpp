#include <cstdio>
#include <gdstk/gdstk.hpp>

using namespace gdstk;

int main() {
  // Create a library (name, unit=1e-6 m, precision=1e-9 m)
  Library lib = {};
  lib.init("test_package", 1e-6, 1e-9);

  // Create a cell
  Cell cell = {};
  cell.name = copy_string("TOP", NULL);

  // Create a rectangle polygon on layer 0, datatype 0
  Polygon rect = rectangle(Vec2{0, 0}, Vec2{10, 5}, make_tag(0, 0));

  // Add polygon to cell, cell to library
  cell.polygon_array.append(&rect);
  lib.cell_array.append(&cell);

  // // Write to GDSII
  // ErrorCode err = lib.write_gds("test_package.gds", 0, NULL);
  // if (err != ErrorCode::NoError) {
  //     printf("Failed to write GDS: error code %d\n", (int)err);
  //     return 1;
  // }
  // printf("Successfully wrote test_package.gds\n");

  // // Read back and verify
  // Library lib2 = read_gds("test_package.gds", 1e-6, 1e-9, NULL, NULL);
  // if (lib2.cell_array.count != 1) {
  //     printf("Verification failed: expected 1 cell, got %d\n",
  //     lib2.cell_array.count); return 1;
  // }
  // printf("Verification passed: read back %d cell(s)\n",
  // lib2.cell_array.count);

  // Clean up
  lib2.clear();
  rect.clear();
  cell.clear();
  lib.clear();
  return 0;
}
