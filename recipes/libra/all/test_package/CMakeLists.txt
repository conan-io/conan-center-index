#
# Copyright 2022 John Harwell, All rights reserved.
#
# SPDX-License Identifier:  MIT
#
# ##############################################################################
# CMake Configuration
# ##############################################################################
# Required by cmake, even though this cmake version handled by conan.
cmake_minimum_required(VERSION 3.31)

project(libra-package-test LANGUAGES CXX)

# ##############################################################################
# CMake Packages
# ##############################################################################
include(libra/project)
