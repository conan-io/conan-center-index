#include <tabulate/table.hpp>
using namespace tabulate;

int main() {
  Table colors;
  colors.add_row({"Font Color is Red", "Font Color is Blue", "Font Color is Green"});
  colors[0][0].format().font_color(Color::red).font_style({FontStyle::bold});
  colors[0][1].format().font_color(Color::blue).font_style({FontStyle::bold});
  colors[0][2].format().font_color(Color::green).font_style({FontStyle::bold});
  std::cout << colors << std::endl;
}

