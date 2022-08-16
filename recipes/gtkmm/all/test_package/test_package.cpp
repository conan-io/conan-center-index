#include <gtkmm/init.h>

#include <iostream>

int main (int argc, char **argv)
{
  Gtk::init_gtkmm_internals();
  std::cout << "Initialized gtkmm." << '\n';

  return 0;
}
