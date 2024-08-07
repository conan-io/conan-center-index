#include <colmap/controllers/option_manager.h>
#include <colmap/scene/reconstruction.h>
#include <colmap/util/logging.h>

int main(int argc, char** argv) {
  colmap::InitializeGlog(argv);
  colmap::OptionManager options;
  options.Parse(argc, argv);
  colmap::Reconstruction reconstruction;
}
