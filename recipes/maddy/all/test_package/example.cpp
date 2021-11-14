/*
 *  This example was copied from https://github.com/progsource/maddy/blob/master/README.md
 */

#include <memory>
#include <string>
#include <cstdlib>

#include <maddy/parser.h>

int main()
{
   std::stringstream markdownInput("");

   // config is optional
   std::shared_ptr<maddy::ParserConfig> config = std::make_shared<maddy::ParserConfig>();
   config->isEmphasizedParserEnabled = true; // default
   config->isHTMLWrappedInParagraph = true;  // default

   std::shared_ptr<maddy::Parser> parser = std::make_shared<maddy::Parser>(config);
   std::string htmlOutput = parser->Parse(markdownInput);

   std::cout << "html:\n" << htmlOutput;

   return EXIT_SUCCESS;
}
