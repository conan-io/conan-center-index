project(testc LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_executable(testc test.c)
target_link_libraries(testc daggy::daggy)
