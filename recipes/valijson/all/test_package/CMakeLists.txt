cmake_minimum_required(VERSION 3.1)
project(test_package)
set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(ValiJSON REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(
	${PROJECT_NAME}
	ValiJSON::valijson
	CONAN_PKG::nlohmann_json
	CONAN_PKG::picojson
	CONAN_PKG::rapidjson
)
