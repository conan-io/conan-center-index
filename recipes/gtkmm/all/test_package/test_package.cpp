#include <gtkmm.h>

#include <iostream>

int main (int argc, char **argv)
{
  auto app = Gtk::Application::create("org.conan.test.gtkmm");
  std::cout << "GTK Application Id: " << app->get_id() << std::endl;

  return 0;
}
