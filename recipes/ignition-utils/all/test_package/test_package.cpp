#include <ignition/utils/cli/CLI.hpp>
#include <ignition/utils/config.hh>



int main(int argc, char** argv)
{
  CLI::App app{"Using ignition-utils CLI wrapper"};

  app.add_flag_callback("-v,--version", [](){
      std::cout << IGNITION_UTILS_VERSION_FULL << std::endl;
      throw CLI::Success();
  });

  CLI11_PARSE(app, argc, argv);
}
