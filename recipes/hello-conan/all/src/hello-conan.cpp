#include <iostream>
#include "hello-conan.h"



void hello_conan(){
    

    #ifdef NDEBUG
    std::cout << "hello-conan: Hello World Release!\n";
    #else
    std::cout << "hello-conan: Hello World Debug!\n";
    #endif

    // ARCHITECTURES
    #ifdef _M_X64
    std::cout << "  hello-conan: _M_X64 defined\n";
    #endif

    #ifdef _M_IX86
    std::cout << "  hello-conan: _M_IX86 defined\n";
    #endif

    #ifdef _M_ARM64
    std::cout << "  hello-conan: _M_ARM64 defined\n";
    #endif

    #if __i386__
    std::cout << "  hello-conan: __i386__ defined\n";
    #endif

    #if __x86_64__
    std::cout << "  hello-conan: __x86_64__ defined\n";
    #endif

    #if __aarch64__
    std::cout << "  hello-conan: __aarch64__ defined\n";
    #endif

    // Libstdc++
    #if defined _GLIBCXX_USE_CXX11_ABI
    std::cout << "  hello-conan: _GLIBCXX_USE_CXX11_ABI "<< _GLIBCXX_USE_CXX11_ABI << "\n";
    #endif

    // MSVC runtime
    #if defined(_DEBUG)
        #if defined(_MT) && defined(_DLL)
        std::cout << "  hello-conan: MSVC runtime: MultiThreadedDebugDLL\n";
        #elif defined(_MT)
        std::cout << "  hello-conan: MSVC runtime: MultiThreadedDebug\n";
        #endif
    #else
        #if defined(_MT) && defined(_DLL)
        std::cout << "  hello-conan: MSVC runtime: MultiThreadedDLL\n";
        #elif defined(_MT)
        std::cout << "  hello-conan: MSVC runtime: MultiThreaded\n";
        #endif
    #endif

    // COMPILER VERSIONS
    #if _MSC_VER
    std::cout << "  hello-conan: _MSC_VER" << _MSC_VER<< "\n";
    #endif

    #if _MSVC_LANG
    std::cout << "  hello-conan: _MSVC_LANG" << _MSVC_LANG<< "\n";
    #endif

    #if __cplusplus
    std::cout << "  hello-conan: __cplusplus" << __cplusplus<< "\n";
    #endif

    #if __INTEL_COMPILER
    std::cout << "  hello-conan: __INTEL_COMPILER" << __INTEL_COMPILER<< "\n";
    #endif

    #if __GNUC__
    std::cout << "  hello-conan: __GNUC__" << __GNUC__<< "\n";
    #endif

    #if __GNUC_MINOR__
    std::cout << "  hello-conan: __GNUC_MINOR__" << __GNUC_MINOR__<< "\n";
    #endif

    #if __clang_major__
    std::cout << "  hello-conan: __clang_major__" << __clang_major__<< "\n";
    #endif

    #if __clang_minor__
    std::cout << "  hello-conan: __clang_minor__" << __clang_minor__<< "\n";
    #endif

    #if __apple_build_version__
    std::cout << "  hello-conan: __apple_build_version__" << __apple_build_version__<< "\n";
    #endif

    // SUBSYSTEMS

    #if __MSYS__
    std::cout << "  hello-conan: __MSYS__" << __MSYS__<< "\n";
    #endif

    #if __MINGW32__
    std::cout << "  hello-conan: __MINGW32__" << __MINGW32__<< "\n";
    #endif

    #if __MINGW64__
    std::cout << "  hello-conan: __MINGW64__" << __MINGW64__<< "\n";
    #endif

    #if __CYGWIN__
    std::cout << "  hello-conan: __CYGWIN__" << __CYGWIN__<< "\n";
    #endif
}

void hello_conan_print_vector(const std::vector<std::string> &strings) {
    for(std::vector<std::string>::const_iterator it = strings.begin(); it != strings.end(); ++it) {
        std::cout << "hello_conan " << *it << std::endl;
    }
}
