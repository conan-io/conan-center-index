# SPDX-FileCopyrightText: 2026 Arnaldo Mendes Pires Junior
# SPDX-License-Identifier: MIT
# pyright: reportOptionalCall=false, reportOptionalMemberAccess=false

"""Consumer test for the ConanCenter GIVP recipe."""

import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout


class GivpTestConan(ConanFile):
    """Build and run a consumer linked to the tested GIVP package."""

    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self) -> None:
        """Use Conan's standard CMake layout for the test consumer."""
        cmake_layout(self)

    def requirements(self) -> None:
        """Require the package instance produced by conan create."""
        self.requires(self.tested_reference_str)

    def build(self) -> None:
        """Configure and compile the CMake consumer."""
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self) -> None:
        """Run the consumer when the build and host platforms match."""
        if can_run(self):
            self.run(os.path.join(self.cpp.build.bindir, "example"), env="conanrun")
