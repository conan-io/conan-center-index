#!/bin/bash
set -e

# Set up path variables
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(realpath "${SCRIPT_DIR}")"
SRC_DIR="${PROJECT_DIR}"
PLATFORM="x86_64"
CONAN_HOST_PROFILE="default"
BUILD_TYPE="Debug"

# Create the cmake command to build based on what the user wants
CMAKE_ARGS=("-H${SRC_DIR}" -DCMAKE_BUILD_TYPE="${BUILD_TYPE}" -DCMAKE_EXPORT_COMPILE_COMMANDS=ON)
CMAKE_PRESET="conan-x86_64-${BUILD_TYPE,,}"

# Set platform specific variables
BUILD_DIR="${SRC_DIR}/build/${PLATFORM}"
INSTALL_DIR="${PROJECT_DIR}/install/${PLATFORM}"

# Install conan deps
set -x
conan_command=(conan install "${SRC_DIR}" --build=missing -s build_type="${BUILD_TYPE}")

# Conditionally append optional settings
conan_command+=(-of "${SRC_DIR}" -pr:h "${CONAN_HOST_PROFILE}" -c tools.cmake.cmake_layout:build_folder_vars="['settings.arch']")
"${conan_command[@]}"

# Run cmake
pushd "${SRC_DIR}"
cmake --preset "${CMAKE_PRESET}" "${CMAKE_ARGS[@]}"
cmake --build --preset "${CMAKE_PRESET}" -- -j 4
popd

# Install files, create appimage if needed
if [ "${BUILD_TYPE}" = "Release" ]; then
    cmake --install "${BUILD_DIR}/${BUILD_TYPE}" --prefix "${INSTALL_DIR}"

    # TODO: AppImage
fi
