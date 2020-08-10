cmake_minimum_required(VERSION 3.1.0)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

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
