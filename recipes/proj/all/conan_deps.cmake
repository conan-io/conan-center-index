macro(custom_find_package name)
    find_package(${name} ${ARGN}
        # Allow only Conan packages
        NO_DEFAULT_PATH
        PATHS ${CMAKE_PREFIX_PATH}
    )
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

