#include "cucumber.hpp"
#include "../src/box.hpp"

BEFORE_T(skip, "@skip") { cuke::skip_scenario(); }

BEFORE(before)
{
  // this runs before every scenario
}
AFTER(after)
{
  // this runs after every scenario
}
BEFORE_STEP(before_step)
{
  // this runs before every step
}
AFTER_STEP(after_step)
{
  // this runs after every step
}

AFTER(close_boxes) { cuke::context<box>().close(); }

AFTER_T(dispatch_box, "@ship or @important")
{
  std::cout << "The box is shipped!" << std::endl;
}

BEFORE_ALL(before_all) { std::cout << "-- Hook before all" << std::endl; }

AFTER_ALL(after_all) { std::cout << "-- Hook after all" << std::endl; }

