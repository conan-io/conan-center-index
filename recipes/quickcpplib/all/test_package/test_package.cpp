#include <iostream>

#include <quickcpplib/uint128.hpp>
#include <quickcpplib/type_traits.hpp>
#include <quickcpplib/tribool.hpp>
#include <quickcpplib/string_view.hpp>
#include <quickcpplib/start_lifetime_as.hpp>
#include <quickcpplib/spinlock.hpp>
#include <quickcpplib/span.hpp>
#include <quickcpplib/signal_guard.hpp>
#include <quickcpplib/scope.hpp>
#include <quickcpplib/ringbuffer_log.hpp>
#include <quickcpplib/revision.hpp>
#include <quickcpplib/packed_backtrace.hpp>
#include <quickcpplib/optional.hpp>
#include <quickcpplib/offset_ptr.hpp>
#include <quickcpplib/memory_resource.hpp>
#include <quickcpplib/mem_flush_loads_stores.hpp>
#include <quickcpplib/in_place_detach_attach.hpp>
#include <quickcpplib/function_ptr.hpp>
#include <quickcpplib/erasure_cast.hpp>
#include <quickcpplib/detach_cast.hpp>
#include <quickcpplib/declval.hpp>
#include <quickcpplib/console_colours.hpp>
#include <quickcpplib/config.hpp>
#include <quickcpplib/byte.hpp>
#include <quickcpplib/bitfield.hpp>
#include <quickcpplib/bit_cast.hpp>
#include <quickcpplib/aligned_allocator.hpp>

#include <quickcpplib/algorithm/bit_interleave.hpp>
#include <quickcpplib/algorithm/bitwise_trie.hpp>
#include <quickcpplib/algorithm/hash.hpp>
#include <quickcpplib/algorithm/memory.hpp>
#include <quickcpplib/algorithm/open_hash_index.hpp>
#include <quickcpplib/algorithm/prime_modulus.hpp>
#include <quickcpplib/algorithm/secded_ecc.hpp>
#include <quickcpplib/algorithm/small_prng.hpp>
#include <quickcpplib/algorithm/string.hpp>

namespace ql = ::quickcpplib;

int main() {
  std::uint64_t x = 20230904ULL;
  std::uint64_t y = 42ULL;
  if( ql::algorithm::hash::fast_hash::hash(reinterpret_cast<const ql::byte::byte*>(&x), sizeof(x))
      == ql::algorithm::hash::fast_hash::hash(reinterpret_cast<const ql::byte::byte*>(&y), sizeof(y)) )
  {
    return -1;
  }

  return 0;
}
