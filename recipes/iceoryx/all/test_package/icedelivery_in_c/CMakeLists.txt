add_executable(iox-c-publisher ice_c_publisher.c)
set_source_files_properties(ice_c_publisher.c PROPERTIES LANGUAGE C)
target_link_libraries(iox-c-publisher iceoryx_binding_c::iceoryx_binding_c)

add_executable(iox-c-subscriber ice_c_subscriber.c)
set_source_files_properties(ice_c_subscriber.c PROPERTIES LANGUAGE C)
target_link_libraries(iox-c-subscriber iceoryx_binding_c::iceoryx_binding_c)
