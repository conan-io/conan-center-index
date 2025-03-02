#include "stacktrace.h"
#include <map>

namespace Nu {

template<typename Type>
struct Alpha {
    struct Beta {
	void func() {
	    print_stacktrace();
	}
	void func(Type) {
	    print_stacktrace();
	}
    };
};

struct Gamma {
    template <int N>
    void unroll(double d) {
	unroll<N-1>(d);
    }
};

template<>
void Gamma::unroll<0>(double) {
    print_stacktrace();
}

} // namespace Nu

int main(void) {
    Nu::Alpha<int>::Beta().func(42);
    Nu::Alpha<char*>::Beta().func("42");
    Nu::Alpha< Nu::Alpha< std::map<int, double> > >::Beta().func();
    Nu::Gamma().unroll<5>(42.0);
    return EXIT_SUCCESS;
}
