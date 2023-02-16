cmake_minimum_required(VERSION 3.8)
project(jpeg-compressor LANGUAGES CXX)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

# jpgd lib
set(JPGD_HDR_LIST ${JPEGCOMPRESSOR_SRC_DIR}/jpgd.h ${JPEGCOMPRESSOR_SRC_DIR}/jpgd_idct.h)
add_library(jpgd ${JPEGCOMPRESSOR_SRC_DIR}/jpgd.cpp)
target_include_directories(jpgd PUBLIC ${JPEGCOMPRESSOR_SRC_DIR})
target_compile_features(jpgd PRIVATE cxx_std_11)

# jpge lib
set(JPGE_HDR_LIST ${JPEGCOMPRESSOR_SRC_DIR}/jpge.h ${JPEGCOMPRESSOR_SRC_DIR}/jpge.h)
add_library(jpge ${JPEGCOMPRESSOR_SRC_DIR}/jpge.cpp)
target_include_directories(jpge PUBLIC ${JPEGCOMPRESSOR_SRC_DIR})
target_compile_features(jpge PRIVATE cxx_std_11)

include(GNUInstallDirs)
install(
    TARGETS jpgd jpge
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES ${JPGD_HDR_LIST} ${JPGE_HDR_LIST} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
