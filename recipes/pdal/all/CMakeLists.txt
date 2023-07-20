cmake_minimum_required(VERSION 3.12)
project(cmake_wrapper)

find_package(Boost REQUIRED filesystem)
link_libraries(Boost::boost Boost::filesystem)

find_package(Eigen3 REQUIRED)
link_libraries(Eigen3::Eigen)

find_package(GDAL REQUIRED)
link_libraries(geotiff_library)

find_package(GeoTIFF REQUIRED)
link_libraries(GDAL::GDAL)

find_package(LASzip)
if(LASzip_FOUND)
    link_libraries(laszip::laszip)
endif()

find_package(LibXml2)
if(LibXml2_FOUND)
    link_libraries(LibXml2::LibXml2)
endif()

find_package(LibXml2 REQUIRED)
link_libraries(LibXml2::LibXml2)

find_package(LibLZMA)
if(LibLZMA_FOUND)
    link_libraries(LibLZMA::LibLZMA)
endif()

find_package(nanoflann REQUIRED)
link_libraries(nanoflann::nanoflann)

#find_package(nlohmann_json REQUIRED)
#link_libraries(nlohmann_json::nlohmann_json)

find_package(OpenSSL REQUIRED)
link_libraries(OpenSSL::SSL)

find_package(ZLIB)
if(ZLIB_FOUND)
    link_libraries(ZLIB::ZLIB)
endif()

find_package(zstd)
if(zstd_FOUND)
    link_libraries(${zstd_LIBRARIES})
endif()

find_package(Libunwind)
if(Libunwind_FOUND)
    link_libraries(libunwind::libunwind)
endif()

add_subdirectory(src)
