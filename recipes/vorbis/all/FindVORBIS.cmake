find_path(
  VORBIS_INCLUDE_DIR
  NAMES
  vorbis
  PATHS
  include)

find_library(
  VORBIS_LIBRARY
  NAMES
  vorbis vorbis_static libvorbis libvorbis_static
  PATHS
  lib)

find_library(
  VORBISFILE_LIBRARY
  NAMES
  vorbisfile vorbisfile_static libvorbisfile libvorbisfile_static
  PATHS
  lib)

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(VORBIS REQUIRED_VARS VORBIS_LIBRARY VORBISFILE_LIBRARY VORBIS_INCLUDE_DIR)

