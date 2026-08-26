# SPDX-FileCopyrightText: 2026 Arnaldo Mendes Pires Junior
# SPDX-License-Identifier: MIT
# mypy: disable-error-code=attr-defined
# pyright: reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportOptionalSubscript=false, reportCallIssue=false, reportArgumentType=false
# pylint: disable=no-member,unsubscriptable-object,invalid-name

"""ConanCenter recipe for the GIVP header-only C++ library."""

import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.0"  # pylint: disable=invalid-name


class GivpConan(ConanFile):
    """Package the released GIVP C++ library for ConanCenter."""

    name = "givp"
    license = "MIT"
    homepage = "https://github.com/Arnime/givp"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "GRASP-ILS-VND with Path Relinking optimizer for continuous and "
        "mixed-integer black-box optimization."
    )
    topics = "optimization", "metaheuristic", "grasp", "ils", "vnd", "header-only"
    package_type = "header-library"

    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self) -> None:
        """Use the upstream CMake project stored in the cpp subdirectory."""
        cmake_layout(self, src_folder="cpp")

    def validate(self) -> None:
        """Reject consumers that do not enable the upstream C++17 requirement."""
        if self.settings.compiler.cppstd:  # type: ignore[attr-defined]  # pylint: disable=no-member
            check_min_cppstd(self, 17)

    def package_id(self) -> None:
        """Make the header-only package independent of consumer settings."""
        self.info.clear()

    def source(self) -> None:
        """Download and verify the immutable upstream release source archive."""
        get(  # pylint: disable=unsubscriptable-object
            self, **self.conan_data["sources"][self.version], strip_root=True
        )

    def generate(self) -> None:
        """Generate the CMake toolchain with optional upstream targets disabled."""
        toolchain = CMakeToolchain(self)
        toolchain.variables["GIVP_BUILD_TESTS"] = False
        toolchain.variables["GIVP_BUILD_BENCHMARKS"] = False
        toolchain.variables["GIVP_BUILD_FUZZ"] = False
        toolchain.generate()

    def build(self) -> None:
        """Configure the released CMake project for installation."""
        cmake = CMake(self)
        cmake.configure()

    def package(self) -> None:
        """Install the CMake package and preserve the upstream license."""
        cmake = CMake(self)
        cmake.install()
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )

    def package_info(self) -> None:
        """Expose the same CMake target shipped by the upstream project."""
        self.cpp_info.set_property("cmake_file_name", "givp")
        self.cpp_info.set_property("cmake_target_name", "givp::givp")
        self.cpp_info.set_property("cmake_find_mode", "config")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
