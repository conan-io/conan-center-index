#include "gici/stream/node_handle.h"
#include "gici/utility/signal_handle.h"
#include "gici/utility/spin_control.h"
#include "gici/utility/node_option_handle.h"

#include <iostream>

using namespace gici;

int main()
{
  std::string data_root = getenv("GICI_DATA");
  std::string config_file = "pseudo_real_time_estimation_DGNSS.yaml";
  std::string config_file_path = data_root + "/" + config_file;
  YAML::Node yaml_node = YAML::LoadFile(config_file_path);
  auto node_option_handle = std::make_shared<NodeOptionHandle>(yaml_node);
  if (!node_option_handle->valid) {
    std::cerr << "Invalid configuration!" << std::endl;
    return -1;
  }
  std::cout << "Successfully loaded " << config_file << std::endl;
  return 0;
}
