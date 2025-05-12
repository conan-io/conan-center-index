#include <Mathter/Geometry.hpp>
#include <Mathter/IoStream.hpp>
#include <Mathter/Matrix.hpp>
#include <Mathter/Quaternion.hpp>
#include <Mathter/Transforms.hpp>
#include <Mathter/Utility.hpp>
#include <Mathter/Vector.hpp>

#include <iostream>

using namespace mathter;


int main() {
	const auto u = Vector(1, 2, 3);
	const auto v = Vector(4, 6, 8);
	const auto r = u + v;
	if (r[0] != 5) {
		std::cout << "Mathter installation failing." << std::endl;
		return 1;
	}
	else {
		std::cout << "Mathter installation works." << std::endl;
		std::cout << "Options:" << std::endl;
#ifdef MATHTER_ENABLE_SIMD
		std::cout << "  with_xsimd = True" << std::endl;
#else
		std::cout << "  with_xsimd = False" << std::endl;
#endif
		return 0;
	}
}
