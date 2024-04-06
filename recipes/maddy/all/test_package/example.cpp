/*
 *  This example was copied from
 * https://github.com/progsource/maddy/blob/master/README.md
 */

#include <cstdlib>
#include <iostream>
#include <memory>
#include <string>

#include <maddy/parser.h>

int main() {
  std::stringstream markdownInput(
      "# Hello world from maddy!\nVisit "
      "[conan-center-index](https://github.com/conan-io/conan-center-index)\n");

  // config is optional
  std::shared_ptr<maddy::ParserConfig> config =
      std::make_shared<maddy::ParserConfig>();
  config->isEmphasizedParserEnabled = true; // default
  config->isHTMLWrappedInParagraph = true;  // default

  std::shared_ptr<maddy::Parser> parser =
      std::make_shared<maddy::Parser>(config);
  std::string htmlOutput = parser->Parse(markdownInput);

  std::cout << "html:\n" << htmlOutput << "\n";

  return EXIT_SUCCESS;
}
