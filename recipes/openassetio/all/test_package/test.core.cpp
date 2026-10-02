#include <openassetio/trait/TraitsData.hpp>

int main() {
  auto traits = openassetio::trait::TraitsData::make();
  traits->setTraitProperty("a", "b", openassetio::Str{"c"});
  return 0;
}
