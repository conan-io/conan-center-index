// Include all headers to test they are where we expect and can be
// compiled.
#include <openassetio/TraitsData.hpp>

int main() {
  auto traits = openassetio::TraitsData::make();
  traits->setTraitProperty("a", "b", openassetio::Str{"c"});
  return 0;
}
