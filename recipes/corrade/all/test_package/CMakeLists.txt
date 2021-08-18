cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Corrade REQUIRED)

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
