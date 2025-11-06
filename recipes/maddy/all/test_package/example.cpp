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
#ifdef MADDY_VERSION_1_4
  config->enabledParsers &= ~maddy::types::EMPHASIZED_PARSER;
  config->enabledParsers |= maddy::types::HTML_PARSER;
#else
  config->isEmphasizedParserEnabled = true; // default
  config->isHTMLWrappedInParagraph = true;  // default
#endif
  std::shared_ptr<maddy::Parser> parser =
      std::make_shared<maddy::Parser>(config);
  std::string htmlOutput = parser->Parse(markdownInput);

  std::cout << "html:\n" << htmlOutput << "\n";

  return EXIT_SUCCESS;
}
