cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

add_executable(${PROJECT_NAME}_shaderc_c test_package_shaderc.c)
target_link_libraries(${PROJECT_NAME}_shaderc_c ${CONAN_LIBS})

add_executable(${PROJECT_NAME}_shaderc_cpp test_package_shaderc.cpp)
target_link_libraries(${PROJECT_NAME}_shaderc_cpp ${CONAN_LIBS})
target_compile_features(${PROJECT_NAME}_shaderc_cpp PRIVATE cxx_std_11)

if(SHADERC_WITH_SPVC)
  add_executable(${PROJECT_NAME}_spvc_c test_package_spvc.c)
  target_link_libraries(${PROJECT_NAME}_spvc_c ${CONAN_LIBS})

  add_executable(${PROJECT_NAME}_spvc_cpp test_package_spvc.cpp)
  target_link_libraries(${PROJECT_NAME}_spvc_cpp ${CONAN_LIBS})
  target_compile_features(${PROJECT_NAME}_spvc_cpp PRIVATE cxx_std_11)
endif()