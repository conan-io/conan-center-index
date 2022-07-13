cmake_minimum_required(VERSION 3.1)
project(flatcc_example)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(flatcc REQUIRED CONFIG)

set(INC_DIR "${PROJECT_SOURCE_DIR}/include")
set(GEN_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(FBS_DIR "${CMAKE_CURRENT_SOURCE_DIR}")

include_directories("${GEN_DIR}" "${INC_DIR}")

add_executable(monster monster.c)

#On MacOS System Integrity Protection (SIP) will clear the DYLD_LIBRARY_PATH variable.
#As a result calling flatcc from cmake will currently not work if the flatcc executable
# is linked shared. As a workaround we generate the flatbuffer C files in the Conan recipe
# when on MacOS and flatcc option 'shared' is True.
if (NOT MACOS_SIP_WORKAROUND)
    add_custom_target(gen_monster_fbs ALL)
    add_custom_command (
        TARGET gen_monster_fbs
        COMMAND cmake -E make_directory "${GEN_DIR}"
        COMMAND flatcc -a -o "${GEN_DIR}" "${FBS_DIR}/monster.fbs"
        DEPENDS flatcc "${FBS_DIR}/monster.fbs"
    )

    add_dependencies(monster gen_monster_fbs)
endif()

target_link_libraries(monster flatcc::flatcc)
