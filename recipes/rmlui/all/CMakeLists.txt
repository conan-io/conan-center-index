cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper LANGUAGES CXX)

if(NOT NO_FONT_INTERFACE_DEFAULT)
    list(APPEND CORE_LINK_LIBS freetype)
endif()

if(BUILD_LUA_BINDINGS)
    find_package(lua REQUIRED CONFIG)
    list(APPEND LUA_BINDINGS_LINK_LIBS lua::lua)
endif()

add_subdirectory(src)

if(NOT NO_THIRDPARTY_CONTAINERS)
    find_package(robin_hood REQUIRED CONFIG)
    target_link_libraries(RmlCore ${LIBRARY_VISIBILITY} robin_hood::robin_hood)
endif()
