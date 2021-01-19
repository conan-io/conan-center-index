#include <morton-nd/mortonND_LUT_encoder.h>

int main() {
  constexpr auto MortonND_3D_64 = mortonnd::MortonNDLutEncoder<5, 12, 4>();
  auto encoding = MortonND_3D_64.Encode(17, 13, 9, 5, 1);
  return 0;
}
