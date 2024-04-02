cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if(WIN32)
  set(FILE2STRING_PATH "${CONAN_BIN_DIRS_DILIGENT-CORE}/File2String.exe")
else()
  set(FILE2STRING_PATH "${CONAN_BIN_DIRS_DILIGENT-CORE}/File2String")
endif()

set(FILE "${CONAN_RES_DIRS_DILIGENT}/HLSLDefinitions.fxh")
set(CONVERTED_FILE "${PROJECT_BINARY_DIR}/HLSLDefinitions.h")

add_custom_command(OUTPUT ${CONVERTED_FILE}
                   COMMAND ${FILE2STRING_PATH} ${FILE} ${CONVERTED_FILE}
                   MAIN_DEPENDENCY ${FILE} # the primary input source file to the command
                   COMMENT "Processing shader ${FILE}"
                   VERBATIM)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
