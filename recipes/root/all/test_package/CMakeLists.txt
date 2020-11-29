cmake_minimum_required(VERSION 3.13)
project(PackageTest CXX)

set(CMAKE_INSTALL_RPATH $ORIGIN)

include(${CMAKE_BINARY_DIR}/conan_paths.cmake)

find_package(Catch2 REQUIRED)
include_directories(${Catch2_INCLUDE_DIRS})

find_package(ROOT REQUIRED)
# include(${ROOT_USE_FILE})

include_directories(${CMAKE_CURRENT_SOURCE_DIR})
ROOT_GENERATE_DICTIONARY(G__Event Particle.hpp Event.hpp OPTIONS -inlineInputHeader LINKDEF EventLinkDef.h )

add_library(Event SHARED Particle.cpp Event.cpp G__Event.cxx)
#add_library(Event SHARED Particle.cpp Event.cpp)
target_link_libraries(Event ROOT::ROOT)

add_executable(example example.cpp)
#target_link_libraries(example Event ROOT::Core ROOT::Hist ROOT::Tree ROOT::Physics ROOT::Thread)
target_link_libraries(example Event ROOT::ROOT)


include(GNUInstallDirs)
install(TARGETS example
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)


# CTest is a testing tool that can be used to test your project.
enable_testing()
add_test(NAME example
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
          COMMAND example)
