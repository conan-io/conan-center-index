cmake_minimum_required(VERSION 3.12)
project(cmake_wrapper)

find_package(Boost REQUIRED CONFIG COMPONENTS filesystem)
link_libraries(Boost::boost Boost::filesystem)

find_package(Eigen3 REQUIRED CONFIG)
link_libraries(Eigen3::Eigen)

find_package(GDAL REQUIRED CONFIG)
link_libraries(geotiff_library)

find_package(GeoTIFF REQUIRED CONFIG)
link_libraries(GDAL::GDAL)

find_package(LibXml2 REQUIRED CONFIG)
link_libraries(LibXml2::LibXml2)

find_package(nanoflann REQUIRED CONFIG)
link_libraries(nanoflann::nanoflann)

find_package(arbiter REQUIRED CONFIG)
link_libraries(arbiter::arbiter)

find_package(nlohmann_json REQUIRED CONFIG)
link_libraries(nlohmann_json::nlohmann_json)
include_directories(BEFORE src/vendor/nlohmann)

find_package(LibLZMA)
if(LibLZMA_FOUND)
    link_libraries(LibLZMA::LibLZMA)
endif()


find_package(LibXml2 QUIET CONFIG)
if(LibXml2_FOUND)
    link_libraries(LibXml2::LibXml2)
endif()

find_package(ZLIB QUIET CONFIG)
if(ZLIB_FOUND)
    link_libraries(ZLIB::ZLIB)
endif()

find_package(zstd QUIET CONFIG)
if(zstd_FOUND)
    link_libraries(${zstd_LIBRARIES})
endif()

find_package(Libunwind QUIET CONFIG)
if(Libunwind_FOUND)
    link_libraries(libunwind::libunwind)
endif()

add_subdirectory(src)
