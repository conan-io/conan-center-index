#include <SevenBit/Conf.hpp>
#include <iostream>

int main(int argc, char **argv) {

  auto configuration = sb::cf::ConfigurationBuilder{}
                           .addAppSettings()
                           .addCommandLine(argc, argv)
                           .addJson({{"setting", "value"}})
                           .build();

  std::cout << "7bitconf version: " << _7BIT_CONF_VERSION << std::endl
            << "Configuration json: " << std::endl
            << *configuration << std::endl;

  return 0;
}
