#include <iostream>
#include <sstream>
#include <string>

#include "replxx.hxx"

int main(int argc, char **argv) {
  using Replxx = replxx::Replxx;
  using namespace std::placeholders;

  std::cout << "Starting Replxx\n";

  Replxx rx;
  rx.install_window_change_handler();

  // set the max number of hint rows to show
  rx.set_max_hint_rows(3);
  rx.bind_key(Replxx::KEY::UP, std::bind(&Replxx::invoke, &rx,
                                         Replxx::ACTION::HISTORY_PREVIOUS, _1));
  rx.bind_key(Replxx::KEY::DOWN, std::bind(&Replxx::invoke, &rx,
                                           Replxx::ACTION::HISTORY_NEXT, _1));

  std::cout << "Exiting Replxx\n";

  return 0;
}
