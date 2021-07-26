cmake_minimum_required(VERSION 3.5)

find_package("iceoryx" REQUIRED)

add_executable(single_process ./single_process.cpp)
target_link_libraries(single_process
    iceoryx_posh::iceoryx_posh_roudi  
    iceoryx_posh::iceoryx_posh
)
