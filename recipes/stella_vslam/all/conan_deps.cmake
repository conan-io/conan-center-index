find_package(tinycolormap REQUIRED CONFIG)
find_package(nlohmann_json REQUIRED CONFIG)

link_libraries(
    tinycolormap::tinycolormap
    nlohmann_json::nlohmann_json
)
