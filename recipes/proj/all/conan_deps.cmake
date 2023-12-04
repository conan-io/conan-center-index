macro(custom_find_package name)
    find_package(${name} ${ARGN}
        # Allow only Conan packages
        NO_DEFAULT_PATH
        PATHS ${CMAKE_PREFIX_PATH}
    )
    string(TOUPPER ${name} name_upper)
    set(${name_upper}_FOUND TRUE)
    set(${name_upper}_VERSION ${${name}_VERSION})
    set(${name_upper}_VERSION_STRING ${${name}_VERSION_STRING})
    set(${name_upper}_INCLUDE_DIRS ${${name}_INCLUDE_DIRS})
    set(${name_upper}_INCLUDE_DIR ${${name}_INCLUDE_DIR})
    set(${name_upper}_LIBRARIES ${${name}_LIBRARIES})
    set(${name_upper}_DEFINITIONS ${${name}_DEFINITIONS})
    unset(name_upper)
endmacro()

custom_find_package(nlohmann_json REQUIRED CONFIG)
link_libraries(nlohmann_json::nlohmann_json)

custom_find_package(SQLite3 REQUIRED CONFIG)
link_libraries(SQLite::SQLite3)

if(ENABLE_TIFF)
    custom_find_package(TIFF QUIET CONFIG)
    link_libraries(TIFF::TIFF)
endif()

if(ENABLE_CURL)
    custom_find_package(CURL QUIET CONFIG)
    link_libraries(CURL::libcurl)
endif()

