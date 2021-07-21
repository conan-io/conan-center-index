add_executable(single_process single_process.cpp)
target_link_libraries(single_process
    iceoryx_posh::iceoryx_posh_roudi
    iceoryx_posh::iceoryx_posh
)
