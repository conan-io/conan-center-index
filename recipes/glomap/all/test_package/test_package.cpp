#include <glomap/controllers/option_manager.h>
#include <glomap/controllers/global_mapper.h>

int main() {
  glomap::OptionManager options;
  glomap::GlobalMapper global_mapper(*options.mapper);
}
