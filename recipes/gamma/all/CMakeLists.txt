cmake_minimum_required(VERSION 3.8)
project(Gamma LANGUAGES CXX)

option(GAMMA_AUDIO_IO "Provide Audio Class" ON)
option(GAMMA_SOUNDFILE "Provide SoundFile Class" ON)

include(GNUInstallDirs)

file(GLOB GAMMA_PUBLIC_HEADERS ${GAMMA_SRC_DIR}/Gamma/*.h)

add_library(Gamma
    ${GAMMA_SRC_DIR}/src/arr.cpp
    ${GAMMA_SRC_DIR}/src/Conversion.cpp
    ${GAMMA_SRC_DIR}/src/Domain.cpp
    ${GAMMA_SRC_DIR}/src/DFT.cpp
    ${GAMMA_SRC_DIR}/src/FFT_fftpack.cpp
    ${GAMMA_SRC_DIR}/src/fftpack++1.cpp
    ${GAMMA_SRC_DIR}/src/fftpack++2.cpp
    ${GAMMA_SRC_DIR}/src/Print.cpp
    ${GAMMA_SRC_DIR}/src/scl.cpp
    ${GAMMA_SRC_DIR}/src/Recorder.cpp
    ${GAMMA_SRC_DIR}/src/Scheduler.cpp
    ${GAMMA_SRC_DIR}/src/Timer.cpp
)
target_include_directories(Gamma PUBLIC ${GAMMA_SRC_DIR})
target_compile_features(Gamma PUBLIC cxx_std_14)
set_target_properties(Gamma PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

find_package(Threads REQUIRED)
target_link_libraries(Gamma PRIVATE Threads::Threads)

include(CheckFunctionExists)
check_function_exists(pow HAVE_MATH_SYSTEM)
if(NOT HAVE_MATH_SYSTEM)
    target_link_libraries(Gamma PRIVATE m)
endif()

if(GAMMA_AUDIO_IO)
    find_package(portaudio REQUIRED CONFIG)
    target_link_libraries(Gamma PRIVATE portaudio::portaudio)
    target_sources(Gamma PRIVATE ${GAMMA_SRC_DIR}/src/AudioIO.cpp)
else()
    list(FILTER GAMMA_PUBLIC_HEADERS EXCLUDE REGEX ".*AudioIO\\.h$")
endif()

if(GAMMA_SOUNDFILE)
    find_package(SndFile REQUIRED CONFIG)
    target_link_libraries(Gamma PRIVATE SndFile::sndfile)
    target_sources(Gamma PRIVATE ${GAMMA_SRC_DIR}/src/SoundFile.cpp)
    target_compile_definitions(Gamma PRIVATE GAM_USE_LIBSNDFILE)
else()
    list(FILTER GAMMA_PUBLIC_HEADERS EXCLUDE REGEX ".*SoundFile\\.h$")
endif()

install(
    TARGETS Gamma
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(FILES ${GAMMA_PUBLIC_HEADERS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/Gamma)
