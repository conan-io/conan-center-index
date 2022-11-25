#include <rpp/rpp.hpp>

#include <functional>
#include <iostream>

int main()
{
    auto observable = rpp::source::from_callable(&::getchar)
                      .repeat()
                      .take_while([](char v) { return v != '0'; })
                      .filter(std::not_fn(&::isdigit))
                      .map(&::toupper);
    return 0;
}
