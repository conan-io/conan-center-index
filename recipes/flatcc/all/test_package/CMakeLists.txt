cmake_minimum_required(VERSION 3.15)
project(flatcc_example LANGUAGES C)

find_package(flatcc REQUIRED CONFIG)

set(INC_DIR "${PROJECT_SOURCE_DIR}/include")
set(GEN_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(FBS_DIR "${CMAKE_CURRENT_SOURCE_DIR}")

include_directories("${GEN_DIR}" "${INC_DIR}")

add_executable(monster monster.c)

add_custom_target(gen_monster_fbs ALL)
add_custom_command (
    TARGET gen_monster_fbs
    COMMAND cmake -E make_directory "${GEN_DIR}"
    COMMAND flatcc -a -o "${GEN_DIR}" "${FBS_DIR}/monster.fbs"
    DEPENDS flatcc "${FBS_DIR}/monster.fbs"
)

add_dependencies(monster gen_monster_fbs)

target_link_libraries(monster flatcc::flatcc)
