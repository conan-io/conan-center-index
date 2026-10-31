#include <flatrate/math.hpp>

#include <iostream>

int main() {
    const double loaded = flatrate::loaded_annual(18290.0);
    const double savings = flatrate::yearly_savings(5995.0, loaded);
    const auto be = flatrate::break_even_months(5995.0, loaded);

    std::cout << "loaded annual: " << loaded << "\n"
              << "yearly savings: " << savings << "\n"
              << "break-even months: " << (be ? std::to_string(*be) : "n/a") << "\n";

    return (loaded > 200000.0 && savings > 100000.0 && be.has_value()) ? 0 : 1;
}
