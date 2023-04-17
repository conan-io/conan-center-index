cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(ValiJSON REQUIRED CONFIG)
find_package(nlohmann_json REQUIRED CONFIG)
find_package(picojson REQUIRED CONFIG)
find_package(RapidJSON REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(
	${PROJECT_NAME}
	PRIVATE
	ValiJSON::valijson
	nlohmann_json::nlohmann_json
	picojson::picojson
	rapidjson
)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
