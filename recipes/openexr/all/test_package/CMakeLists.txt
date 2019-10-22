cmake_minimum_required(VERSION 2.8.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if(MSVC)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
endif()

add_executable(${PROJECT_NAME}
  drawImage.cpp
  generalInterfaceExamples.cpp
  generalInterfaceTiledExamples.cpp
  lowLevelIoExamples.cpp
  test_package.cpp
  previewImageExamples.cpp
  rgbaInterfaceExamples.cpp
  rgbaInterfaceTiledExamples.cpp
)

target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
