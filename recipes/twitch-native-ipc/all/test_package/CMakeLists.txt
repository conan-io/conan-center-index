cmake_minimum_required(VERSION 3.15)
project(PackageTest)

find_package(twitch-native-ipc REQUIRED CONFIG)

add_executable(example example.c)
target_link_libraries(example twitch-native-ipc::twitch-native-ipc)

add_executable(example2 example2.cpp)
target_link_libraries(example2 twitch-native-ipc::twitch-native-ipc)
target_compile_features(example2 PRIVATE cxx_std_17)
