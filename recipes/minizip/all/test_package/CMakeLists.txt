cmake_minimum_required(VERSION 3.1.0)
project(test_package)

function(test_and_set_compile_definition definitioname)
	if(${definitioname})
		target_compile_definitions(${PROJECT_NAME} PRIVATE ${definitioname})
	endif()
endfunction()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

configure_file(TESTDATA ${CMAKE_CURRENT_BINARY_DIR})

test_and_set_compile_definition(MZ_ZIP_NO_DECOMPRESSION)
test_and_set_compile_definition(MZ_ZIP_NO_COMPRESSION)
test_and_set_compile_definition(HAVE_BZIP2)
test_and_set_compile_definition(HAVE_LZMA)
test_and_set_compile_definition(HAVE_ZSTD)
test_and_set_compile_definition(HAVE_ZLIB)
test_and_set_compile_definition(HAVE_COMPAT)
test_and_set_compile_definition(HAVE_PKCRYPT)
test_and_set_compile_definition(HAVE_WZAES)
test_and_set_compile_definition(MZ_ZIP_NO_ENCRYPTION)
