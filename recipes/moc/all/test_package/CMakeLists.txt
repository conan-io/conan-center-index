cmake_minimum_required(VERSION 3.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Moc REQUIRED CONFIG)
include(Moc)


set(CMAKE_PROJECT_VARS
    CONAN_MOC_ROOT
    MOC_TOOL
)

foreach(MOC_VAR ${CMAKE_PROJECT_VARS})
    message("${MOC_VAR}: ${${MOC_VAR}}")
    if(NOT ${MOC_VAR})
        message(FATAL_ERROR "${MOC_VAR} NOT FOUND")
    endif()
endforeach()

set(TARGET_GEN_SRC_DIR ${CMAKE_CURRENT_BINARY_DIR}/genSrc)
file(MAKE_DIRECTORY ${TARGET_GEN_SRC_DIR})

bld_add_custom_moc_target(${CMAKE_SOURCE_DIR}/test_app.moc
    SET_VAR MOC_GEN_SRC_FILES
    INCLUDE ${CMAKE_SOURCE_DIR}
    TEMPLATE ${CMAKE_SOURCE_DIR}/test_app.tpl
    DEPENDS_ON ${CMAKE_SOURCE_DIR}/test_app.moh
    OUTPUT ${TARGET_GEN_SRC_DIR}
  )

add_executable(${CMAKE_PROJECT_NAME}
  main.cpp
  ${MOC_GEN_SRC_FILES}
  )

target_include_directories(${CMAKE_PROJECT_NAME}
  PRIVATE ${TARGET_GEN_SRC_DIR}/include
  )

target_link_libraries(${CMAKE_PROJECT_NAME} ${CONAN_LIBS})
