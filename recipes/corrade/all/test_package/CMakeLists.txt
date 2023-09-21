cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(Corrade REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} Corrade::Main)
if(VERSION_2019_10)
	target_compile_definitions(${PROJECT_NAME} PRIVATE VERSION_2019_10)
endif()
if(WITH_UTILITY)
	target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_UTILITY)
	target_link_libraries(${PROJECT_NAME} Corrade::Utility)
endif()

set_target_properties(${PROJECT_NAME}
    PROPERTIES
    	CXX_STANDARD 11
    	CXX_STANDARD_REQUIRED ON
    	CXX_EXTENSIONS OFF
)
