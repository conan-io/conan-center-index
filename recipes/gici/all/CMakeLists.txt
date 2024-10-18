cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper CXX)

add_subdirectory(src)

install(TARGETS gici rtklib vikit_common svo fast
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
)
install(TARGETS gici_main RUNTIME DESTINATION bin)
install(DIRECTORY src/include/ DESTINATION include)
install(DIRECTORY src/third_party/fast/include/ DESTINATION include/gici/third_party)
install(DIRECTORY src/third_party/rtklib/include/ DESTINATION include/gici/third_party)
install(DIRECTORY src/third_party/rpg_svo/include/ DESTINATION include/gici/third_party)
install(DIRECTORY src/third_party/rpg_vikit/vikit_common/include/ DESTINATION include/gici/third_party)
install(DIRECTORY src/option/ DESTINATION res)
