# SPDX-FileCopyrightText: 2026 Arnaldo Mendes Pires Junior
# SPDX-License-Identifier: MIT

"""Conan recipe for the GIVP C++ header-only package."""

import os
import re
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    # Conan modules are optional in generic Python type-check environments.
    from conan import ConanFile as ConanFileBase  # type: ignore[import-not-found]
    from conan.tools.cmake import CMake as CMakeHelper  # type: ignore[import-not-found]
    from conan.tools.cmake import (  # type: ignore[import-not-found]
        cmake_layout as cmake_layout_helper,
    )
    from conan.tools.files import copy as copy_helper  # type: ignore[import-not-found]
else:
    import importlib

    ConanFileBase = importlib.import_module("conan").ConanFile
    _cmake_tools = importlib.import_module("conan.tools.cmake")
    CMakeHelper = _cmake_tools.CMake
    cmake_layout_helper = _cmake_tools.cmake_layout
    copy_helper = importlib.import_module("conan.tools.files").copy


class GivpConan(ConanFileBase):
    """GRASP-ILS-VND with Path Relinking optimizer for C++17."""

    DEFAULT_VERSION: ClassVar[str] = "1.0.0"
    _SEMVER_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$"
    )

    name: ClassVar[str] = "givp"
    version: str
    license: ClassVar[str] = "MIT"
    author: ClassVar[str] = "Arnaldo Mendes Pires Junior"
    url: ClassVar[str] = "https://github.com/Arnime/grasp_ils_vnd_pr"
    homepage: ClassVar[str] = "https://github.com/Arnime/grasp_ils_vnd_pr"
    description: ClassVar[str] = (
        "GRASP-ILS-VND with Path Relinking optimizer for continuous and "
        "mixed-integer black-box optimization. Header-only C++17 library."
    )
    topics: ClassVar[tuple[str, ...]] = (
        "optimization",
        "metaheuristic",
        "grasp",
        "ils",
        "vnd",
        "header-only",
    )

    settings: ClassVar[tuple[str, ...]] = ("os", "compiler", "build_type", "arch")
    generators: ClassVar[tuple[str, ...]] = ("CMakeToolchain",)
    options: ClassVar[dict[str, Any]] = {}
    default_options: ClassVar[dict[str, Any]] = {}

    no_copy_source: ClassVar[bool] = True

    @classmethod
    def _normalized_version(cls, value: str) -> str:
        candidate = value.strip()
        if candidate.startswith("v"):
            candidate = candidate[1:]
        if cls._SEMVER_PATTERN.match(candidate):
            return candidate
        return ""

    def set_version(self) -> None:
        """Resolve version from CI/workflow env with a safe fallback."""
        supplied_version = self._normalized_version(
            str(getattr(self, "version", "") or "")
        )
        env_version = self._normalized_version(os.getenv("GIVP_VERSION", ""))
        tag_version = self._normalized_version(os.getenv("GITHUB_REF_NAME", ""))
        self.version = (
            supplied_version or env_version or tag_version or self.DEFAULT_VERSION
        )

    def export_sources(self) -> None:
        """Export the C++ sources needed by the package from the parent cpp tree."""
        cpp_root = os.path.abspath(os.path.join(self.recipe_folder, ".."))
        repo_root = os.path.abspath(os.path.join(cpp_root, ".."))
        copy_helper(
            self,
            "*.hpp",
            src=os.path.join(cpp_root, "include"),
            dst=os.path.join(self.export_sources_folder, "include"),
            keep_path=True,
        )
        copy_helper(
            self,
            "*.h",
            src=os.path.join(cpp_root, "include"),
            dst=os.path.join(self.export_sources_folder, "include"),
            keep_path=True,
        )
        copy_helper(
            self,
            "*.cmake.in",
            src=os.path.join(cpp_root, "cmake"),
            dst=os.path.join(self.export_sources_folder, "cmake"),
            keep_path=True,
        )
        copy_helper(
            self,
            "CMakeLists.txt",
            src=cpp_root,
            dst=self.export_sources_folder,
            keep_path=False,
        )
        copy_helper(
            self,
            "LICENSE",
            src=repo_root,
            dst=self.export_sources_folder,
            keep_path=False,
        )

    def layout(self) -> None:
        """Configure layout for Conan 2."""
        cmake_layout_helper(self, src_folder=".")

    def build(self) -> None:
        """Configure CMake so package() can run install() from the prepared build tree."""
        cmake = CMakeHelper(self)
        cmake.configure(
            variables={
                "GIVP_BUILD_TESTS": False,
                "GIVP_BUILD_BENCHMARKS": False,
                "GIVP_BUILD_FUZZ": False,
            }
        )

    def package(self) -> None:
        """Install the header-only library with the same CMake package layout used elsewhere."""
        cmake = CMakeHelper(self)
        cmake.install()

    def package_info(self) -> None:
        """Define package information for consumers."""
        self.cpp_info.set_property("cmake_file_name", "givp")
        self.cpp_info.set_property("cmake_target_name", "givp::givp")
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_find_mode", "config")
        self.cpp_info.cxxflags = []
        self.cpp_info.cflags = []
