#include <arg_router/arg_router.hpp>

namespace ar = arg_router;
namespace arp = ar::policy;

#if (__cplusplus >= 202002L)
using namespace ar::literals;

int main(int argc, char *argv[]) {
  ar::root(
      arp::validation::default_validator,
      ar::help("help"_S, "h"_S, "Display this help and exit"_S,
               arp::program_name_t{"just-cats"_S},
               arp::program_intro_t{"Prints cats!"_S},
               arp::program_addendum_t{"An example program for arg_router."_S}),
      ar::flag("cat"_S, "English cat"_S,
               arp::router{[](bool) { std::cout << "cat" << std::endl; }}),
      ar::flag("猫"_S, //
               arp::description_t{"日本語の猫"_S},
               arp::router{[](bool) { std::cout << "猫" << std::endl; }}),
      ar::flag("🐱"_S, //
               arp::description_t{"Emoji cat"_S},
               arp::router{[](bool) { std::cout << "🐱" << std::endl; }}),
      ar::flag("แมว"_S, //
               "แมวไทย"_S,
               arp::router{[](bool) { std::cout << "แมว" << std::endl; }}),
      ar::flag("кіт"_S, //
               "український кіт"_S,
               arp::router{[](bool) { std::cout << "кіт" << std::endl; }}))
      .parse(argc, argv);

  return EXIT_SUCCESS;
}
#else
int main(int argc, char *argv[]) {
  ar::root(
      arp::validation::default_validator,
      ar::help(S_("help"){}, S_('h'){}, S_("Display this help and exit"){},
               arp::program_name<S_("just-cats")>,
               arp::program_intro<S_("Prints cats!")>,
               arp::program_addendum<S_("An example program for arg_router.")>),
      ar::flag(S_("cat"){}, //
               S_("English cat"){},
               arp::router{[](bool) { std::cout << "cat" << std::endl; }}),
      ar::flag(S_("猫"){}, //
               arp::description<S_("日本語の猫")>,
               arp::router{[](bool) { std::cout << "猫" << std::endl; }}),
      ar::flag(S_("🐱"){}, //
               arp::description<S_("Emoji cat")>,
               arp::router{[](bool) { std::cout << "🐱" << std::endl; }}),
      ar::flag(S_("แมว"){}, //
               S_("แมวไทย"){},
               arp::router{[](bool) { std::cout << "แมว" << std::endl; }}),
      ar::flag(S_("кіт"){}, //
               S_("український кіт"){},
               arp::router{[](bool) { std::cout << "кіт" << std::endl; }}))
      .parse(argc, argv);

  return EXIT_SUCCESS;
}
#endif
