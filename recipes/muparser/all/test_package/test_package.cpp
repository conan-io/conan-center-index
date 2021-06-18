#include <iostream>

#include "muParser.h"

// Function callback
double MySqr(double a_fVal)
{
  return a_fVal*a_fVal;
}

// main program
int main(int argc, char* argv[])
{
  using namespace mu;

  try
  {
    double fVal = 1;
    Parser p;
    p.DefineVar("a", &fVal);
    p.DefineFun("MySqr", MySqr);
    p.SetExpr("MySqr(a)*_pi+min(10,a)");

    for (std::size_t a=0; a<100; ++a)
    {
      fVal = a;  // Change value of variable a
      std::cout << p.Eval() << std::endl;
    }
  }
  catch (Parser::exception_type &e)
  {
    std::cout << e.GetMsg() << std::endl;
  }
  return 0;
}
