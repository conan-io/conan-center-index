find_path(
  OPUS_INCLUDE_DIR
  NAMES
  opus.h
  PATHS
  include)

find_library(
  OPUS_LIBRARY
  NAMES
  opus
  libopus
  PATHS
  lib)

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(OPUS REQUIRED_VARS OPUS_LIBRARY OPUS_INCLUDE_DIR)
