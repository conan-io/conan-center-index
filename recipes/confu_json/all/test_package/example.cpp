#include "confu_json/confu_json.hxx"
#include <boost/json/src.hpp> // this file should be included only in one translation unit

BOOST_FUSION_DEFINE_STRUCT((shared_class), Nested,
                           (long, answer)) // used to define a struct

int main() {
  using namespace confu_json;
  auto nested = shared_class::Nested{};
  nested.answer = 42;
  std::cout << to_json(nested)
            << std::endl; // converts the struct into json and prints it
  auto nestedTest = to_object<shared_class::Nested>(
      to_json(nested)); // converts the struct into json and back into an object
  assert(nested.answer == nestedTest.answer);
}
