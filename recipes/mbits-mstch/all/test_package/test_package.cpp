#include <cstdio>
#include <mstch/mstch.hpp>

int main() {
  mstch::map root{
      {"it", "works"},
      {"happy", true},
      {"various",
       mstch::array{
           mstch::map{{"value", nullptr}},
           mstch::map{{"value", 0ll}},
           mstch::map{{"value", 3.14}},
           mstch::map{{"value", false}},
       }},
  };

  puts(mstch::render(R"(>>> It {{it}}
    I'm {{^happy}}not {{/happy}}happy about it.
    Various:
{{#various}}
        - {{value}};
{{/various}}
)",
                     root)
           .c_str());
}
