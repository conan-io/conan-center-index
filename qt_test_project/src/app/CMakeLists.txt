# ==============================================
# Targets

# App target
qt_add_executable(geojsonviewer src/main.cpp)

target_link_libraries(
    geojsonviewer
    PUBLIC ${LIBRARY_NAME}

        Qt6::Core
        Qt6::Gui
        Qt6::LocationPrivate
        Qt6::Positioning
        Qt6::Qml
        Qt6::Quick
        Qt6::Svg
        Qt6::Multimedia

        ffmpeg::avutil
        ffmpeg::avdevice
        ffmpeg::avfilter
        ffmpeg::avformat
        ffmpeg::avcodec
        ffmpeg::swscale
        ffmpeg::swresample

        libva::libva

        SDL2::SDL2main
        SDL2::SDL2-static
    )

target_compile_options(
    geojsonviewer
    PUBLIC -Wall
           -Wextra
           -Wpedantic
           -fPIC)

target_compile_features(geojsonviewer PUBLIC cxx_std_17)

# target_link_options(navx PRIVATE "-Wl,--copy-dt-needed-entries")

# ==============================================
# Resources

# Bundle Resources
set(qml_resource_files
    "res/qml/GeoJsonDelegate.qml"
    "res/qml/main.qml"
    "res/qml/mapitems/CircleItem.qml"
    "res/qml/mapitems/PolygonItem.qml"
    "res/qml/mapitems/PolylineItem.qml"
    "res/qml/mapitems/RectangleItem.qml")
set(svg_resource_files "res/svg/lightbulb.svg")
set(font_resource_files "res/font/Roboto-Regular.ttf")

qt6_add_resources(
    geojsonviewer
    "qml"
    PREFIX
    "/"
    BASE
    "res/qml"
    FILES
    ${qml_resource_files})
qt6_add_resources(
    geojsonviewer
    "other"
    PREFIX
    "/"
    BASE
    "res"
    FILES
    ${svg_resource_files}
    ${font_resource_files})

# ==============================================
# Install

install(
    TARGETS geojsonviewer
    RUNTIME DESTINATION "bin"
    LIBRARY DESTINATION "lib")
