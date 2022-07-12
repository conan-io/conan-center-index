#include <xqilla/xqilla-simple.hpp>

int main() {

  XQilla xqilla;
  auto context = xqilla.createContext();
   
  if(!context) {
    return 1;
  }

  return 0;
   
}
