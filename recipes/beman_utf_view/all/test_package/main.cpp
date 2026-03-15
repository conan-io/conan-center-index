// SPDX-License-Identifier: BSL-1.0

//   Copyright Eddie Nolan and Jonathan Wakely 2023 - 2025.
// Distributed under the Boost Software License, Version 1.0.
//    (See accompanying file LICENSE.txt or copy at
//          https://www.boost.org/LICENSE_1_0.txt)

#include <beman/utf_view/code_unit_view.hpp>
#include <beman/utf_view/detail/fake_inplace_vector.hpp>
#include <beman/utf_view/endian_view.hpp>
#include <beman/utf_view/null_term.hpp>
#include <beman/utf_view/to_utf_view.hpp>
#include <algorithm>
#include <array>
#include <cstdlib>
#include <filesystem>
#include <functional>
#include <iterator>
#include <optional>
#include <ranges>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace beman::utf_view::examples {

using namespace std::string_view_literals;

template <typename CharT>
std::basic_string<CharT> sanitize(CharT const* str) {
  return null_term(str) | to_utf<CharT> | std::ranges::to<std::basic_string<CharT>>();
}

std::optional<char32_t> last_nonascii(std::ranges::view auto str) {
  for (auto c : str | as_char8_t | to_utf32 | std::views::reverse |
           std::views::filter([](char32_t c) { return c > 0x7f; })) {
    return c;
  }
  return std::nullopt;
}

#ifdef _MSC_VER
bool windows_path() {
  std::vector<int> path_as_ints = {U'C', U':', U'\x00010000'};
  std::filesystem::path path =
      path_as_ints | as_char32_t | std::ranges::to<std::u32string>();
  const auto& native_path = path.native();
  if (native_path != std::wstring{L'C', L':', L'\xD800', L'\xDC00'}) {
    return false;
  }
  return true;
}
#endif

std::u8string as_char32_t_example() {
  auto get_icu_code_points = [] { return std::vector<int>{0x1F574, 0xFFFD}; };
  std::vector<int> input = get_icu_code_points();
  // This is ill-formed without the as_char32_t adaptation.
  auto input_utf8 = input | as_char32_t | to_utf8 | std::ranges::to<std::u8string>();
  return input_utf8;
}

std::string enum_to_string(utf_transcoding_error ec) {
  switch (ec) {
  case utf_transcoding_error::truncated_utf8_sequence:
    return "truncated_utf8_sequence";
  case utf_transcoding_error::unpaired_high_surrogate:
    return "unpaired_high_surrogate";
  case utf_transcoding_error::unpaired_low_surrogate:
    return "unpaired_low_surrogate";
  case utf_transcoding_error::unexpected_utf8_continuation_byte:
    return "unexpected_utf8_continuation_byte";
  case utf_transcoding_error::overlong:
    return "overlong";
  case utf_transcoding_error::encoded_surrogate:
    return "encoded_surrogate";
  case utf_transcoding_error::out_of_range:
    return "out_of_range";
  case utf_transcoding_error::invalid_utf8_leading_byte:
    return "invalid_utf8_leading_byte";
  }
  std::unreachable();
}

template <typename FromChar, typename ToChar>
std::basic_string<ToChar> transcode_or_throw(std::basic_string_view<FromChar> input) {
  std::basic_string<ToChar> result;
  auto view = input | to_utf_or_error<ToChar>;
  for (auto it = view.begin(), end = view.end(); it != end; ++it) {
    if ((*it).has_value()) {
      result.push_back(**it);
    } else {
      throw std::runtime_error("error at position " +
                               std::to_string(it.base() - input.begin()) + ": " +
                               enum_to_string((*it).error()));
    }
  }
  return result;
}

#if 0
// Deliberately broken by double-transcode optimization in the CPO
template <typename I, typename O>
using transcode_result = std::ranges::in_out_result<I, O>;

template <std::input_iterator I, std::sentinel_for<I> S, std::output_iterator<char8_t> O>
transcode_result<I, O> transcode_to_utf32(I first, S last, O out) {
  auto r = std::ranges::subrange(first, last) | to_utf32;

  auto copy_result = std::ranges::copy(r, out);

  return transcode_result<I, O>{copy_result.in.base(), copy_result.out};
}

bool transcode_to_utf32_test() {
  std::u8string_view char8_string{u8"\xf0\x9f\x95\xb4\xef\xbf\xbd"};
  auto utf16_transcoding_view{char8_string | to_utf16};
  std::u32string char32_string{};
  auto transcode_result{transcode_to_utf32(utf16_transcoding_view.begin(),
                                           utf16_transcoding_view.end(),
                                           std::back_insert_iterator{char32_string})};
  auto expected_in_it{utf16_transcoding_view.begin()};
  std::ranges::advance(expected_in_it, 3);
  if (expected_in_it != transcode_result.in) {
    return false;
  }
  return true;
}
#endif

#ifndef _MSC_VER
enum class suit : std::uint8_t {
  spades = 0xA,
  hearts = 0xB,
  diamonds = 0xC,
  clubs = 0xD
};

// Unicode playing card characters are laid out such that changing the second least
// significant nibble changes the suit, e.g.
// U+1F0A1 PLAYING CARD ACE OF SPADES
// U+1F0B1 PLAYING CARD ACE OF HEARTS
constexpr char32_t change_playing_card_suit(char32_t card, suit s) {
  if (U'\N{PLAYING CARD ACE OF SPADES}' <= card && card <= U'\N{PLAYING CARD KING OF CLUBS}') {
    return (card & ~(0xF << 4)) | (static_cast<std::uint8_t>(s) << 4);
  }
  return card;
}

bool change_playing_card_suit_test() {
  std::u8string_view const spades = u8"🂡🂢🂣🂤🂥🂦🂧🂨🂩🂪🂫🂭🂮";
  std::u8string const hearts =
    spades |
    to_utf32 |
    std::views::transform(std::bind_back(change_playing_card_suit, suit::hearts)) |
    to_utf8 |
    std::ranges::to<std::u8string>();
  if (hearts != u8"🂱🂲🂳🂴🂵🂶🂷🂸🂹🂺🂻🂽🂾") {
    return false;
  }
  return true;
}
#endif

#ifdef __cpp_lib_containers_ranges
static_assert(std::string{std::from_range, "Brubeck" | std::views::take(5)} == "Brube");
// static_assert(std::string{std::from_range, "Dave" | std::views::take(5)} == "Dave"); // fails
using namespace std::string_view_literals;
static_assert(std::string{std::from_range, "Dave" | std::views::take(5)} == "Dave\0"sv); // passes
static_assert(std::is_same_v<std::remove_reference_t<decltype("foo")>, const char[4]>);
static_assert(std::ranges::equal("foo", std::array{'f', 'o', 'o', '\0'}));
constexpr std::string take_five_a(char const* long_string) {
  std::string_view const long_string_view = long_string; // read all of long_string!
  return std::string{std::from_range, long_string_view | std::views::take(5)};
}
constexpr std::string take_five_b(char const* long_string) {
  std::ranges::subrange const long_string_range(long_string, null_sentinel); // lazy!
  return std::string{std::from_range, long_string_range | std::views::take(5)};
}
constexpr std::string take_five_c(char const* long_string) {
  return std::string{std::from_range, null_term(long_string) | std::views::take(5)};
}
static_assert(take_five_a("Dave") == "Dave"sv); // passes
static_assert(take_five_a("Brubeck") == "Brube"sv); // passes
static_assert(take_five_b("Dave") == "Dave"sv); // passes
static_assert(take_five_b("Brubeck") == "Brube"sv); // passes
static_assert(take_five_c("Dave") == "Dave"sv); // passes
static_assert(take_five_c("Brubeck") == "Brube"sv); // passes
#endif

#ifndef _MSC_VER
static_assert((u8"\xf0\x9f\x99\x82"sv | to_utf32 | std::ranges::to<std::u32string>()) == U"\x0001F642");
static_assert((u8"\xf0\x9f\x99\x82"sv | std::views::take(3) | to_utf32 | std::ranges::to<std::u32string>()) == U"�");
static_assert(
  *(u8"\xf0\x9f\x99\x82"sv | std::views::take(3) | to_utf32_or_error).begin() ==
  std::unexpected{utf_transcoding_error::truncated_utf8_sequence});
#endif

#ifndef _MSC_VER
bool basis_operation() {
  std::u8string invalid_utf8{u8"\xf0\x9f\x99\x82\xf0\x9f\x99"};
  auto to_utf8_1{invalid_utf8 | to_utf8 | std::ranges::to<std::u8string>()};
  auto to_utf8_2{
    invalid_utf8
    | to_utf8_or_error
    | std::views::transform(
        [](std::expected<char8_t, utf_transcoding_error> c)
          -> detail::fake_inplace_vector<char8_t, 3>
        {
          if (c.has_value()) {
            return {c.value()};
          } else {
            // U+FFFD
            return {u8'\xEF', u8'\xBF', u8'\xBD'};
          }
        })
    | std::views::join
    | std::ranges::to<std::u8string>()};
  return to_utf8_1 == to_utf8_2;
}

static_assert(
  !std::ranges::equal(u8"foo"sv | to_utf32, std::array{U'f', U'o', U'o', U'\0'}));
static_assert(
  std::ranges::equal(u8"foo"sv | to_utf32, std::array{U'f', U'o', U'o'}));
#endif

template <typename FromCharT, typename ToCharT>
std::basic_string<ToCharT> transcode_to(std::basic_string<FromCharT> const& input) {
  return input | to_utf<ToCharT> | std::ranges::to<std::basic_string<ToCharT>>();
}

#if __cpp_lib_ranges_chunk >= 202202L
std::u8string parse_message_subset(
    std::span<std::byte> message, std::size_t offset, std::size_t length) {
  return std::span{message.begin() + offset, message.begin() + offset + length}
         | std::views::chunk(2)
         | std::views::transform(
             [](const auto chunk) {
               std::array<std::byte, 2> a{};
               std::ranges::copy(chunk, a.begin());
               return std::bit_cast<std::uint16_t>(a);
             })
         | from_big_endian
         | as_char16_t
         | to_utf8
         | std::ranges::to<std::u8string>();
}
#endif

bool readme_examples() {
  using namespace std::string_view_literals;
#ifndef _MSC_VER
  std::u32string hello_world =
      u8"こんにちは世界"sv | to_utf32 | std::ranges::to<std::u32string>();
  if (hello_world != U"こんにちは世界") {
    return false;
  }
  if (sanitize(u8"\xc2") != u8"\xef\xbf\xbd") {
    return false;
  }
  if (last_nonascii("hôtel"sv).value() != U'ô') {
    return false;
  }
  if (as_char32_t_example() != u8"\xf0\x9f\x95\xb4\xef\xbf\xbd") {
    return false;
  }
  auto foo = transcode_or_throw<char8_t, char32_t>(u8"\xf0\x9f\x95\xb4\xef\xbf\xbd");
  auto bar = std::u32string{U"\x0001F574\uFFFD"};
  if (foo != bar) {
    return false;
  }
  try {
    transcode_or_throw<char8_t, char32_t>(u8"\xc3\xa9\xff");
    return false;
  } catch (std::exception const& e) {
    if (e.what() != "error at position 2: invalid_utf8_leading_byte"sv) {
      return false;
    }
  }
  if (!change_playing_card_suit_test()) {
    return false;
  }
  if (!basis_operation()) {
    return false;
  }
#else
  if (!windows_path()) {
    return false;
  }
#endif
  if (transcode_to<char8_t, char32_t>(u8"foo") != U"foo") {
    return false;
  }
#ifndef _MSC_VER // TODO: figure out why this test fails on MSVC
#if __cpp_lib_ranges_chunk >= 202202L
  std::array<std::byte, 6> message{
    std::byte{0x12}, std::byte{0xD8}, std::byte{0x3D}, std::byte{0xDE}, std::byte{0x42},
    std::byte{0x34}};
  if (!std::ranges::equal(u8"\xf0\x9f\x99\x82"sv, parse_message_subset(message, 1, 4))) {
    return false;
  }
#endif
#endif
  return true;
}

} // namespace beman::utf_view::examples

void windows_function(std::ranges::view auto) {

}

void foo(std::ranges::view auto v) {
  windows_function(v | beman::utf_view::to_utf16);
}

int main(int, char const* argv[]) {
  foo(beman::utf_view::null_term(argv[1]) | beman::utf_view::as_char8_t | beman::utf_view::to_utf32);
  return beman::utf_view::examples::readme_examples() ? EXIT_SUCCESS : EXIT_FAILURE;
}
