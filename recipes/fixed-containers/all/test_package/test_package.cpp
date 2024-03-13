#include "fixed_containers/fixed_vector.hpp"
#include "fixed_containers/enum_utils.hpp"

enum class ColorBackingEnum : int {
  RED,
  YELLOW,
  GREEN,
  BLUE,
};

class Color : public fixed_containers::rich_enums::SkeletalRichEnum<Color, ColorBackingEnum> {
  friend SkeletalRichEnum::ValuesFriend;
  using SkeletalRichEnum::SkeletalRichEnum;

public:
  inline static constexpr const std::array<Color, count()>& values() {
    return ::fixed_containers::rich_enums::SkeletalRichEnumValues<Color>::VALUES;
  }

  FIXED_CONTAINERS_RICH_ENUM_CONSTANT_GEN_HELPER(Color, RED);
  FIXED_CONTAINERS_RICH_ENUM_CONSTANT_GEN_HELPER(Color, YELLOW);
  FIXED_CONTAINERS_RICH_ENUM_CONSTANT_GEN_HELPER(Color, GREEN);
  FIXED_CONTAINERS_RICH_ENUM_CONSTANT_GEN_HELPER(Color, BLUE);
};

int main(void) {
  constexpr auto v1 = []() {
    fixed_containers::FixedVector<int, 11> v{};
    v.push_back(0);
    v.emplace_back(1);
    v.push_back(2);
    return v;
  }();
  static_assert(v1[0] == 0);
  static_assert(v1[1] == 1);
  static_assert(v1[2] == 2);
  static_assert(v1.size() == 3);
  static_assert(v1.capacity() == 11);

  static_assert(fixed_containers::rich_enums::is_rich_enum<Color>);
  auto constexpr const COLOR = Color::RED();
  static_assert("RED" == COLOR.to_string());

  return 0;
}
