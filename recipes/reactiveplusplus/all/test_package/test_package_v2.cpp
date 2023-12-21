// Source: https://github.com/victimsnino/ReactivePlusPlus/tree/v2/docs#operators

#include <rpp/rpp.hpp>

#include <iostream>

int main()
{
  rpp::source::from_callable(&::getchar)
    | rpp::operators::repeat()
    | rpp::operators::take_while([](char v) { return v != '0'; })
    | rpp::operators::filter(std::not_fn(&::isdigit))
    | rpp::operators::map(&::toupper);

  return 0;
}
