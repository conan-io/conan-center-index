cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME}_shaderc_c test_package_shaderc.c)
target_link_libraries(${PROJECT_NAME}_shaderc_c ${CONAN_LIBS})

add_executable(${PROJECT_NAME}_shaderc_cpp test_package_shaderc.cpp)
target_link_libraries(${PROJECT_NAME}_shaderc_cpp ${CONAN_LIBS})
set_property(TARGET ${PROJECT_NAME}_shaderc_cpp PROPERTY CXX_STANDARD 11)

if(SHADERC_WITH_SPVC)
  add_executable(${PROJECT_NAME}_spvc_c test_package_spvc.c)
  target_link_libraries(${PROJECT_NAME}_spvc_c ${CONAN_LIBS})

  add_executable(${PROJECT_NAME}_spvc_cpp test_package_spvc.cpp)
  target_link_libraries(${PROJECT_NAME}_spvc_cpp ${CONAN_LIBS})
  set_property(TARGET ${PROJECT_NAME}_spvc_cpp PROPERTY CXX_STANDARD 11)
endif()
