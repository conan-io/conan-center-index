#include <cds/init.h>
#include <cds/gc/hp.h>

int main() {
  cds::Initialize();
  {
    cds::gc::HP hpGC;
    cds::threading::Manager::attachThread();
  }
  cds::Terminate();
  return 0;
}
