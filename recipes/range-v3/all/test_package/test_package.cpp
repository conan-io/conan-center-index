#include <range/v3/all.hpp>
#include <iostream>

using namespace ranges;

#if RANGE_V3_MINOR > 5
using test_sentinel_t = default_sentinel_t;
#else
using test_sentinel_t = v3::default_sentinel;
#endif

// A range that iterates over all the characters in a
// null-terminated string.
class c_string_range
  : public view_facade<c_string_range>
{
    friend range_access;
    char const * sz_;
    char const & read() const { return *sz_; }
    bool equal(::test_sentinel_t) const { return *sz_ == '\0'; }
    void next() { ++sz_; }
public:
    c_string_range() = default;
    explicit c_string_range(char const *sz) : sz_(sz)
    {
        assert(sz != nullptr);
    }
};

int main()
{
    c_string_range r("hello world");
    // Iterate over all the characters and print them out
    ranges::for_each(r, [](char ch){
        std::cout << ch << ' ';
    });
    // prints: h e l l o   w o r l d
}
