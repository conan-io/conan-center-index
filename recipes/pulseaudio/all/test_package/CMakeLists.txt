cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(PulseAudio REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE ${PULSEAUDIO_LIBRARY})
target_include_directories(${PROJECT_NAME} PRIVATE ${PULSEAUDIO_INCLUDE_DIR})
# Alternatively, can also use the unofficial Conan target
# target_link_libraries(${PROJECT_NAME} PRIVATE pulseaudio::pulseaudio)
