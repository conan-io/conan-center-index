#include <iostream>
#include <fstream>

#include "MiniScript/SimpleString.h"
#include "MiniScript/UnicodeUtil.h"
#include "MiniScript/SimpleVector.h"
#include "MiniScript/List.h"
#include "MiniScript/Dictionary.h"
#include "MiniScript/MiniscriptParser.h"
#include "MiniScript/MiniscriptInterpreter.h"

#ifdef MINISCRIPT_1_6

int main() {
  MiniScript::Interpreter interp;

  interp.standardOutput = [](MiniScript::String s, bool lineBreak=true) { std::cout << s.c_str() << std::endl; };
  interp.errorOutput = [](MiniScript::String s, bool lineBreak=true) { std::cerr << s.c_str() << std::endl; };
  interp.implicitOutput = [](MiniScript::String s, bool lineBreak=true) { std::cout << s.c_str() << std::endl; };

  interp.REPL("x = 5");
  interp.REPL("print \"x = \" + x");
  interp.REPL("y = 5 + x");
  interp.REPL("print \"y = \" + y");

  return 0;
}

#else

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

#endif
