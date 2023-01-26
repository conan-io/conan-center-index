#include <cstdio>
#include <utf/utf.hpp>
#include <utf/version.hpp>

using namespace utf;
using namespace std::literals;

static constexpr auto smiley8sv = "\360\237\230\200"sv;
static constexpr auto smiley16 = u"\U0001F600"sv;

int main() {
  std::printf("Uses utf/%s\n", version.to_string().c_str());
  if (!utf::is_valid(smiley8sv))
    std::fprintf(stderr, "smiley8s is invalid...\n");
  if (!utf::is_valid(smiley16))
    std::fprintf(stderr, "smiley16 is invalid...\n");
  if (utf::as_str8(smiley16) != smiley8sv)
    std::fprintf(stderr, "smiley16 differs from \"%.*s\"\n",
                 (int)smiley8sv.length(), smiley8sv.data());
}
