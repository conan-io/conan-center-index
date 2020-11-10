cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

include("conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

# Set include paths
conan_global_flags()

# Setup libraries to link
set(Z3_LIBRARIES CONAN_PKG::z3)
set(PCRE_LIBRARY CONAN_PKG::pcre)

add_subdirectory(source_subfolder)
