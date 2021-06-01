cmake_minimum_required(VERSION 3.12)
project(test_package)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

find_package(Moc REQUIRED)

set(TARGET_GEN_SRC_DIR ${CMAKE_CURRENT_BINARY_DIR}/genSrc)

bld_add_custom_moc_target(${CMAKE_SOURCE_DIR}/test_app.moc
    SET_VAR MOC_GEN_SRC_FILES
    INCLUDE ${CMAKE_SOURCE_DIR}
    TEMPLATE ${CMAKE_SOURCE_DIR}/test_app.tpl
    DEPENDS_ON ${CMAKE_SOURCE_DIR}/test_app.moh
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/genSrc
  )

add_executable(${PROJECT_NAME}
  main.cpp
  ${MOC_GEN_SRC_FILES}
  )

target_include_directories(${PROJECT_NAME}
  PRIVATE ${TARGET_GEN_SRC_DIR})

target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
