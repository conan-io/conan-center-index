#include <libmeshb7.h>

#include <stdio.h>

int main() {
   int64_t OutMsh;
   if(!(OutMsh = GmfOpenMesh("test.meshb", GmfWrite, 2, 3)))
      return 1;
   GmfCloseMesh(OutMsh);
   puts("Success! Created test.meshb");
   return 0;
}