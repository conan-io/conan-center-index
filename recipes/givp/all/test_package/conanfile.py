# SPDX-FileCopyrightText: 2026 Arnaldo Mendes Pires Junior
# SPDX-License-Identifier: MIT

"""Conan recipe for the GIVP C++ header-only package."""

# pyright: reportMissingImports=false

import os

from conan import ConanFile  # type: ignore[import-not-found]
from conan.tools.cmake import CMake, cmake_layout  # type: ignore[import-not-found]


class GivpTestConan(ConanFile):
    """Test package for givp library."""

    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self) -> None:
        """ "Use CMake layout for the test package."""
        cmake_layout(self)

    def requirements(self) -> None:
        """Require the library being tested."""
        self.requires(self.tested_reference_str)

    def build(self) -> None:
        """Build the test package."""
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self) -> None:
        """Run the test package."""
        self.run(os.path.join(self.cpp.build.bindir, "example"))
