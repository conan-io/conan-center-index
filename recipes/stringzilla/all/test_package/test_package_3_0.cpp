#include <cstdlib>
#include <iostream>

#include "stringzilla/stringzilla.hpp"

namespace sz = ashvardanian::stringzilla;

int main(void) {
  sz::string haystack = "some string";
  sz::string_view needle = sz::string_view(haystack).substr(0, 4);

  auto substring_position = haystack.find(needle); // Or `rfind`

  haystack.end() - haystack.begin() == haystack.size(); // Or `rbegin`, `rend`
  haystack.find_first_of(" \w\t") == 4; // Or `find_last_of`, `find_first_not_of`, `find_last_not_of`
  haystack.starts_with(needle) == true; // Or `ends_with`
  haystack.remove_prefix(needle.size()); // Why is this operation in-place?!

  return EXIT_SUCCESS;
}
