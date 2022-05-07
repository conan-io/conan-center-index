#include <SI/electric_charge.h>
#include <SI/mass.h>

using namespace SI::literals;

constexpr auto one_kilogram = 1.0_kg;
constexpr auto ten_coulomb = 5.0_A * 2.0_s;
constexpr auto half_an_ampere = ten_coulomb / 20.0_s;

void calculate_mass(const SI::kilo_gram_t<long double> &kg) {
  // do something meaningful here
}

int main(int, char **) {
  calculate_mass(one_kilogram);
  return 0;
}
