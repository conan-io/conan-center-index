cmake_minimum_required(VERSION 3.1)
project(semver.c C)

if (CONAN_STATIC)
  add_library(semver.c STATIC source_subfolder/semver.c)
else()
  add_library(semver.c SHARED source_subfolder/semver.c)
endif()
