#include <iostream>
#include <fstream>

#include "MiniScript/SimpleString.h"
#include "MiniScript/UnicodeUtil.h"
#include "MiniScript/SimpleVector.h"
#include "MiniScript/List.h"
#include "MiniScript/Dictionary.h"
#include "MiniScript/MiniscriptParser.h"
#include "MiniScript/MiniscriptInterpreter.h"

int main() {
  MiniScript::Interpreter interp;

  interp.standardOutput = [](MiniScript::String s) { std::cout << s.c_str() << std::endl; };
  interp.errorOutput = [](MiniScript::String s) { std::cerr << s.c_str() << std::endl; };
  interp.implicitOutput = [](MiniScript::String s) { std::cout << s.c_str() << std::endl; };

  interp.REPL("x = 5");
  interp.REPL("print \"x = \" + x");
  interp.REPL("y = 5 + x");
  interp.REPL("print \"y = \" + y");

  return 0;
}
