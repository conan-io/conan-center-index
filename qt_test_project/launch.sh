#!/bin/bash
set -e

# Set up path variables
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

source "${SCRIPT_DIR}/build/x86_64/Debug/generators/conanrunenv-debug-x86_64.sh"
INSTALL_DIR_ARG="${SCRIPT_DIR}/build/x86_64/Debug"

# Export INSTALL_DIR
INSTALL_DIR_ABS="$(realpath "${INSTALL_DIR_ARG}")"
export INSTALL_DIR="${INSTALL_DIR_ABS}"

export QT_MEDIA_BACKEND=ffmpeg
export QT_FFMPEG_DECODING_HW_DEVICE_TYPES="vaapi"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${INSTALL_DIR}/lib:${INSTALL_DIR}/thirdparty"
export SYSTEM_LIBVA_DRIVERS_PATH="/usr/lib/x86_64-linux-gnu/dri/"
export BUNDLED_LIBVA_DRIVERS_PATH="${INSTALL_DIR}/thirdparty/dri"
export LIBVA_DRIVERS_PATH="${SYSTEM_LIBVA_DRIVERS_PATH}"
export LIBVA_DRIVER_NAME="iHD" 
export QT_FFMPEG_DEBUG=1
echo $LD_LIBRARY_PATH

"${INSTALL_DIR}/src/app/qtffmpegtest"