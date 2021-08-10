/* Tutorial from NSIMD library, modified to use a constant string */

#include <nsimd/nsimd-all.hpp>

#include <string>
#include <vector>
#include <iostream>

#include <assert.h>
#include <string.h>

template <typename T>
void uppercase_scalar(T *dst, const T *src, int n) {
  for (int i = 0; i < n; i++) {
    if (src[i] >= 'a' && src[i] <= 'z') {
      dst[i] = src[i] + ('A' - 'a');
    } else {
      dst[i] = src[i];
    }
  }
}

template <typename T>
void uppercase_simd(T *dst, const T *src, int n) {
  using namespace nsimd;
  typedef pack<T> p_t;
  typedef packl<T> pl_t;
  int l = len<p_t>();

  int i;
  for (i = 0; i + l <= n; i += l) {
    p_t text = loadu<p_t>(src + i);
    pl_t mask = text >= 'a' && text <= 'z';
    p_t then_pack = text + ('A' - 'a');
    p_t TEXT = if_else(mask, then_pack, text);
    storeu(dst + i, TEXT);
  }

  pl_t mask = mask_for_loop_tail<pl_t>(i, n);
  p_t text = maskz_loadu(mask, src + i);
  p_t TEXT = if_else(text >= 'a' && text <= 'z', text + ('A' - 'a'), text);
  mask_storeu(mask, dst + i, TEXT);
}

int main() {
  std::string input("The quick brown fox jumps over the lazy dog");

  std::cout << "Original text         : " << input << std::endl;

  std::vector<i8> dst_scalar(input.size() + 1);
  uppercase_scalar(&dst_scalar[0], (i8 *)input.c_str(), (int)input.size());
  std::cout << "Scalar uppercase text: " << &dst_scalar[0] << std::endl;

  std::vector<i8> dst_simd(input.size() + 1);
  uppercase_simd(&dst_simd[0], (i8 *)input.c_str(), (int)input.size());
  std::cout << "NSIMD uppercase text : " << &dst_simd[0] << std::endl;

  assert(memcmp(&dst_scalar[0], &dst_simd[0], dst_simd.size()) == 0);

  return 0;
}
