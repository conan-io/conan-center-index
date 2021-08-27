#include <peglib.h>

#include <assert.h>
#include <iostream>

int main() {
  // (2) Make a parser
  peg::parser parser(R"(
      # Grammar for Calculator...
      Additive    <- Multitive '+' Additive / Multitive
      Multitive   <- Primary '*' Multitive / Primary
      Primary     <- '(' Additive ')' / Number
      Number      <- < [0-9]+ >
      %whitespace <- [ \t]*
  )");

  assert((bool)parser == true);

  // (3) Setup actions
  parser["Additive"] = [](const peg::SemanticValues &sv) {
      switch (sv.choice()) {
      case 0:  // "Multitive '+' Additive"
          return peg::any_cast<int>(sv[0]) + peg::any_cast<int>(sv[1]);
      default: // "Multitive"
          return peg::any_cast<int>(sv[0]);
      }
  };

  parser["Multitive"] = [](const peg::SemanticValues &sv) {
      switch (sv.choice()) {
      case 0:  // "Primary '*' Multitive"
          return peg::any_cast<int>(sv[0]) * peg::any_cast<int>(sv[1]);
      default: // "Primary"
          return peg::any_cast<int>(sv[0]);
      }
  };

  parser["Number"] = [](const peg::SemanticValues &sv) {
      return std::stoi(sv.token(), nullptr, 10);
  };

  // (4) Parse
  parser.enable_packrat_parsing(); // Enable packrat parsing.

  int val;
  parser.parse(" (1 + 2) * 3 ", val);

  assert(val == 9);
}
