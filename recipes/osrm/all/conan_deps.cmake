macro(custom_find_package name)
    find_package(${name} ${ARGN}
        # Allow only Conan packages
        NO_DEFAULT_PATH
        PATHS ${CMAKE_PREFIX_PATH}
    )
    string(TOUPPER ${name} name_upper)
    set(${name_upper}_FOUND TRUE)
    set(${name_upper}_VERSION_STRING ${${name}_VERSION_STRING})
    set(${name_upper}_INCLUDE_DIRS ${${name}_INCLUDE_DIRS})
    set(${name_upper}_INCLUDE_DIR ${${name}_INCLUDE_DIR})
    set(${name_upper}_LIBRARIES ${${name}_LIBRARIES})
    set(${name_upper}_DEFINITIONS ${${name}_DEFINITIONS})
    unset(name_upper)
endmacro()

custom_find_package(Boost REQUIRED)
custom_find_package(BZip2 REQUIRED)
custom_find_package(EXPAT REQUIRED)
custom_find_package(lua REQUIRED)
custom_find_package(TBB REQUIRED)
custom_find_package(Osmium REQUIRED)
link_libraries(libosmium::libosmium)

set(Boost_CHRONO_LIBRARY Boost::chrono)
set(Boost_DATE_TIME_LIBRARY Boost::date_time)
set(Boost_FILESYSTEM_LIBRARY Boost::filesystem)
set(Boost_IOSTREAMS_LIBRARY Boost::iostreams)
set(Boost_REGEX_LIBRARY Boost::regex)
set(Boost_SYSTEM_LIBRARY Boost::system Boost::program_options)
set(Boost_THREAD_LIBRARY Boost::thread)
set(Boost_ZLIB_LIBRARY ZLIB::ZLIB)

# unvendored deps
custom_find_package(microtar REQUIRED)
link_libraries(microtar::microtar)

custom_find_package(mapbox-variant REQUIRED)
link_libraries(mapbox-variant::mapbox-variant)

custom_find_package(mapbox-geometry REQUIRED)
link_libraries(mapbox-geometry::mapbox-geometry)

custom_find_package(fmt REQUIRED)
link_libraries(fmt::fmt)

custom_find_package(RapidJSON REQUIRED)
link_libraries(rapidjson)

custom_find_package(FlatBuffers REQUIRED)
if(TARGET flatbuffers::flatbuffers_shared)
    link_libraries(flatbuffers::flatbuffers_shared)
else()
    link_libraries(flatbuffers::flatbuffers)
endif()

custom_find_package(sol2 REQUIRED)
link_libraries(sol2::sol2)
