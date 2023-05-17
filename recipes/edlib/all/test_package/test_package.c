#include <edlib.h>

#include <stdio.h>

int main() {
  EdlibAlignResult result = edlibAlign("hello", 5, "world!", 6, edlibDefaultAlignConfig());
  printf("edit_distance('hello', 'world!') = %d\n", result.editDistance);
  edlibFreeAlignResult(result);
  return 0;
}
