#include <iostream>
#include "Test.h"

int main()
{
  Test::Test message;
  Test::Test_mref ref = message.ref();
  std:: cout << ref.get_String().c_str() << "\n";
}
