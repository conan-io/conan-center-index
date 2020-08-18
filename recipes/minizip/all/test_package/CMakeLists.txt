cmake_minimum_required(VERSION 3.1.0)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

# Additional link test for UNIX
if(UNIX)
add_executable(${PROJECT_NAME}_with_explicit_bsd-ctor test_package.c)
target_link_libraries(${PROJECT_NAME}_with_explicit_bsd-ctor CONAN_PKG::minizip CONAN_LIB::libbsd_bsd-ctor)
target_compile_definitions(${PROJECT_NAME}_with_explicit_bsd-ctor PRIVATE
    CONAN_MZ_VERSION=\"${CONAN_MZ_VERSION}\"
    ${HAVE_COMPRESS}
    ${HAVE_DECOMPRESS}
    ${HAVE_BZIP2}
    ${HAVE_LZMA}
    ${HAVE_ZSTD}
    ${HAVE_ZLIB}
    ${HAVE_COMPAT}
    ${HAVE_PKCRYPT}
    ${HAVE_WZAES}
    ${HAVE_ENCRYPTION})
endif()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} CONAN_PKG::minizip)
target_compile_definitions(${PROJECT_NAME} PRIVATE
    CONAN_MZ_VERSION=\"${CONAN_MZ_VERSION}\"
    ${HAVE_COMPRESS}
    ${HAVE_DECOMPRESS}
    ${HAVE_BZIP2}
    ${HAVE_LZMA}
    ${HAVE_ZSTD}
    ${HAVE_ZLIB}
    ${HAVE_COMPAT}
    ${HAVE_PKCRYPT}
    ${HAVE_WZAES}
    ${HAVE_ENCRYPTION})
