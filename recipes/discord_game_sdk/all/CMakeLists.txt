cmake_minimum_required(VERSION 3.15)
project(discord_game_sdk_cpp CXX)

find_library(SDK_LIB discord_game_sdk PATHS "${SDK_LIB_FOLDER}" NO_DEFAULT_PATH)

file(GLOB SRC_FILES "${CMAKE_CURRENT_SOURCE_DIR}/cpp/*.cpp")

add_library(discord_game_sdk_cpp STATIC ${SRC_FILES})
target_link_libraries(discord_game_sdk_cpp PUBLIC ${SDK_LIB})
set_property(TARGET discord_game_sdk_cpp PROPERTY CXX_STANDARD 11)

install(TARGETS discord_game_sdk_cpp ARCHIVE DESTINATION lib)
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/cpp/" DESTINATION include FILES_MATCHING PATTERN "*.h")
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/c/discord_game_sdk.h" DESTINATION include)
