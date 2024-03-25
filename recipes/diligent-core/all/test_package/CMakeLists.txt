cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(diligent-core REQUIRED CONFIG)

set(DILIGENT_CORE_RES_DIR "${core_INCLUDE_DIR}/../res")
set(FILE "${DILIGENT_CORE_RES_DIR}/HLSLDefinitions.fxh")
set(CONVERTED_FILE "${PROJECT_BINARY_DIR}/HLSLDefinitions.h")

add_custom_command(OUTPUT ${CONVERTED_FILE}
                   COMMAND File2String ${FILE} ${CONVERTED_FILE}
                   MAIN_DEPENDENCY ${FILE} # the primary input source file to the command
                   COMMENT "Processing shader ${FILE}"
                   VERBATIM)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} diligent-core::diligent-core)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
