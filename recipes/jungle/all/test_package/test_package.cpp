#include <libjungle/jungle.h>

#include <cassert>
#include <iostream>

int main(void) {
  jungle::DB *dbInst;
  jungle::Status s;
  jungle::DBConfig db_config;

  s = jungle::DB::open(&dbInst, ".", db_config);

  assert(s.ok());

  std::cout << "Success\n";
  return 0;
}
