cmake_minimum_required(VERSION 3.8)
project(OpenFBX LANGUAGES CXX)

find_package(miniz REQUIRED CONFIG)

add_library(OpenFBX ${OPENFBX_SRC_DIR}/src/ofbx.cpp)
target_compile_features(OpenFBX PUBLIC cxx_std_11)
set_target_properties(OpenFBX PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
target_link_libraries(OpenFBX PRIVATE miniz::miniz)

install(TARGETS OpenFBX
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(FILES ${OPENFBX_SRC_DIR}/src/ofbx.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
