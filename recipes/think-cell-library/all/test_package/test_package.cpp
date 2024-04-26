
// think-cell public library
//
// Copyright (C) 2016-2018 think-cell Software GmbH
//
// Distributed under the Boost Software License, Version 1.0.
// See accompanying file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt

#include "tc/range/meta.h"
#include "tc/range/filter_adaptor.h"
#include "tc/string/format.h"
#include "tc/string/make_c_str.h"

#include <boost/range/adaptors.hpp>

#include <vector>
#include <cstdio>

namespace {

template <typename... Args>
void print(Args&&... args) noexcept {
	std::printf("%s", tc::implicit_cast<char const*>(tc::make_c_str<char>(std::forward<Args>(args)...)));
}

//---- Basic ------------------------------------------------------------------------------------------------------------------
void basic () {
	std::vector<int> v = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20};

	tc::for_each(
		tc::filter(v, [](const int& n){ return (n%2==0);}),
		[&](auto const& n) {
			print(tc::as_dec(n), ", ");
		}
	);
	print("\n");
}

//---- Generator Range --------------------------------------------------------------------------------------------------------
namespace {
	struct generator_range {
		template< typename Func >
		void operator()( Func func ) const& {
			for(int i=0;i<50;++i) {
				func(i);
			}
		}
	};
}

void ex_generator_range () {
	tc::for_each( tc::filter( generator_range(), [](int i){ return i%2==0; } ), [](int i) {
		print(tc::as_dec(i), ", ");
	});
	print("\n");
}

//---- Generator Range (with break) -------------------------------------------------------------------------------------------
namespace {
	struct generator_range_break {
		template< typename Func >
		tc::break_or_continue operator()( Func func ) const& {
			using namespace tc;
			for(int i=0;i<5000;++i) {
				if (func(i)==break_) { return break_; }
			}
			return continue_;
		}
	};
}

void ex_generator_range_break () {
	tc::for_each( tc::filter( generator_range_break(), [](int i){ return i%2==0; } ), [](int i) -> tc::break_or_continue {
		print(tc::as_dec(i), ", ");
		return (i>=50)? tc::break_ : tc::continue_;
	});
	print("\n");
}

//---- Stacked filters --------------------------------------------------------------------------------------------------------
void stacked_filters() {
	tc::for_each( tc::filter( tc::filter( tc::filter(
								generator_range_break(),
								[](int i){ return i%2!=0; } ),
								[](int i){ return i%3!=0; } ),
								[](int i){ return i%5!=0; } )
			, [](int i) -> tc::break_or_continue
	{
		print(tc::as_dec(i), ", ");
		return (i>25)? tc::break_ : tc::continue_;
	});
	print("\n");
}

}

int main() {
	print("-- Running Examples ----------\n");

	basic();
	ex_generator_range();
	ex_generator_range_break();
	stacked_filters();

	using namespace tc;

	int av[] = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20};
	auto v = std::vector<int> (av, av+sizeof(av)/sizeof(int));

	//---- filter example with iterators  -------------------------------------------

	auto r =  tc::filter( tc::filter( tc::filter(
								v,
								[](int i){ return i%2!=0; } ),
								[](int i){ return i%3!=0; } ),
								[](int i){ return i%5!=0; } );

	for (auto it = std::begin(r),
				end = std::end(r);
		it != end;
		++it)
	{
		print(tc::as_dec(*it), ", ");
	}
	print("\n");

	//---- boost for comparison -----------------------------------------------------

	auto br = v | boost::adaptors::filtered([](int i){ return i%2!=0; })
				| boost::adaptors::filtered([](int i){ return i%3!=0; })
				| boost::adaptors::filtered([](int i){ return i%5!=0; });


	for (auto it = std::begin(br),
		end = std::end(br);
		it != end;
		++it)
	{
		print(tc::as_dec(*it), ", ");
	}
	print("\n");

	print("-- Done ----------\n");
	std::fflush(stdout);

	return EXIT_SUCCESS;
}
