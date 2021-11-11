#include <iostream>

int main(int argc, char *argv[]) {




#if defined(_GLIBCXX_USE_CXX11_ABI)
    std::cout << "_GLIBCXX_USE_CXX11_ABI is " << _GLIBCXX_USE_CXX11_ABI << "." << std::endl;
#else
    std::cout << "_GLIBCXX_USE_CXX11_ABI is undefined." << std::endl;
#endif

#if defined(_GLIBCXX_USE_DUAL_ABI)
    std::cout << "_GLIBCXX_USE_DUAL_ABI is " << _GLIBCXX_USE_DUAL_ABI << "." << std::endl;
#else
    std::cout << "_GLIBCXX_USE_DUAL_ABI is undefined." << std::endl;
#endif

#if defined(__GNUG__)
    std::cout << "__GNUG__ is defined." << std::endl;
#else
    std::cout << "__GNUG__ is undefined." << std::endl;
#endif

#if defined(_LIBCPP_VERSION)
    std::cout << "_LIBCPP_VERSION is " << _LIBCPP_VERSION << "." << std::endl;
#else
    std::cout << "_LIBCPP_VERSION is undefined." << std::endl;
#endif


#if defined(_GLIBCXX_USE_CXX11_ABI)
#if _GLIBCXX_USE_CXX11_ABI || (defined(_GLIBCXX_USE_DUAL_ABI) && !_GLIBCXX_USE_DUAL_ABI)
#define XTENSOR_GLIBCXX_USE_CXX11_ABI 1
    std::cout << "XTENSOR_GLIBCXX_USE_CXX11_ABI is defined" << std::endl;

#endif
#endif

#if !defined(__GNUG__) || defined(_LIBCPP_VERSION) || defined(XTENSOR_GLIBCXX_USE_CXX11_ABI)
    std::cout << "use is_trivially_default_constructible" << std::endl;
#else
    std::cout << "use has_trivial_default_constructor" << std::endl;
#endif

#if defined(_GLIBCXX_RELEASE)
    std::cout << "_GLIBCXX_RELEASE is " << _GLIBCXX_RELEASE << std::endl;
#else
    std::cout << "_GLIBCXX_RELEASE is undefined." << std::endl;
#endif


  return 0;
}
