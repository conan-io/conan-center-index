#include <iostream>
#include <ignition/utils/cli/CLI.hpp>
#include <ignition/utils/config.hh>
#include <ignition/utils/SuppressWarning.hh>


int main(int argc, char** argv)
{
  std::cout << "Hello from ignition-utils test_package\n";
  CLI::App app{"Using ignition-utils CLI wrapper"};

  app.add_flag_callback("-v,--version", [](){
      std::cout << IGNITION_UTILS_VERSION_FULL << std::endl;
      throw CLI::Success();
  });

  CLI11_PARSE(app, argc, argv);
}
