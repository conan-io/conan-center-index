#include <cstdio>
#include <diags/sources.hpp>
#include <diags/version.hpp>

using namespace diags;
using namespace std::literals;

namespace app {
enum class str { in_use };
UNPACK_DIAGS_TYPES(diags::string::singular<str>);
SINGLE_FORM_DIAGS_SUPPORT(str)

struct strings : translator_type {
  std::string_view get(str id) const noexcept final {
    switch (id) {
    case str::in_use:
      return "Library is in use"sv;
    }
    return {};
  }
  std::string_view get(severity sev) const noexcept final {
    switch (sev) {
    case severity::note:
      return "note"sv;
    case severity::warning:
      return "warning"sv;
    case severity::error:
      return "error"sv;
    case severity::fatal:
      return "fatal"sv;
    default:
      break;
    }
    return {};
  }
};

location_range_severity pos_from(source_code &source,
                                 severity sev = severity::note) {
  auto const start = source.position(1, 13);
  auto const stop = start.moved_by(0, 7);
  return start - stop[sev];
}
} // namespace app

int main() {
  app::strings strings{};
  sources host{};
  auto src = host.source("use-diags.cpp");

  host.set_contents("use-diags.cpp", "- underline [range] in brackets"sv);
  auto msg = app::pos_from(src)
             << format("{}: {}", app::str::in_use, version.to_string());
  host.push_back(msg);

  auto tr = strings.make();
  host.set_printer<printer>(&get_stdout(), tr, color::always, link_type::gcc);
  host.print_diagnostics();
}
