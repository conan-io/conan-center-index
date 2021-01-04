#include <string>
#include "kainjow/mustache.hpp"


int main() {
  using namespace kainjow::mustache;

  mustache tmpl{"{{#employees}}{{name}}{{#comma}}, {{/comma}}{{/employees}}"};
  data employees{data::type::list};
  employees
    << object{{"name", "Steve"}, {"comma", true}}
    << object{{"name", "Bill"}};

  if( tmpl.render({"employees", employees}) == "Steve, Bill" ) {
    return 0;
  }
  return 1;
}
