if (MSVC)
	cmake_minimum_required(VERSION 3.10)	# to be able to set C++17
else()
	cmake_minimum_required(VERSION 3.8)		# to be able to set C++17
endif(MSVC)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example example.cpp)