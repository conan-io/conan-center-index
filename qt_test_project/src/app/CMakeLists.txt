# ==============================================
# Targets

# App target
qt_add_executable(qtffmpegtest src/main.cpp)

target_link_libraries(
    qtffmpegtest
    PUBLIC ${LIBRARY_NAME}
        Qt6::Gui
        Qt6::OpenGL
        Qt6::Xml
        Qt6::Svg
        Qt6::Network
        Qt6::Quick
        Qt6::QuickControls2
        Qt6::Multimedia
        Qt6::Qml
        Qt6::Sql
        Qt6::Widgets

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
    qtffmpegtest
    PUBLIC -Wall
           -Wextra
           -Wpedantic
           -fPIC)

target_compile_features(qtffmpegtest PUBLIC cxx_std_17)


# ==============================================
# Resources

# Bundle Resources
set(qml_resource_files
    "res/qml/main.qml")
set(svg_resource_files "res/svg/lightbulb.svg")

qt6_add_resources(
    qtffmpegtest
    "qml"
    PREFIX
    "/"
    BASE
    "res/qml"
    FILES
    ${qml_resource_files})
qt6_add_resources(
    qtffmpegtest
    "other"
    PREFIX
    "/"
    BASE
    "res"
    FILES
    ${svg_resource_files})

# ==============================================
# Install

install(
    TARGETS qtffmpegtest
    RUNTIME DESTINATION "bin"
    LIBRARY DESTINATION "lib")
