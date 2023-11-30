import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, replace_in_file, save
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class RmmConan(ConanFile):
    name = "rmm"
    description = "RAPIDS Memory Manager"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rapidsai/rmm"
    topics = ("cuda", "memory-management", "memory-allocation", "rapids", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        # Based partially on https://github.com/rapidsai/rmm/tree/v23.06.00#get-rmm-dependencies
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "9.3",
            "clang": "8",
            "apple-clang": "14.0",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("thrust/1.17.2")
        self.requires("spdlog/1.12.0")
        self.requires("fmt/10.1.1")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def lazy_lt_semver(v1, v2):
            # Needed to allow version "9" >= "9.3" for gcc
            return all(int(p1) < int(p2) for p1, p2 in zip(str(v1).split("."), str(v2).split(".")))

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and lazy_lt_semver(self.settings.compiler.version, minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.dependencies["thrust"].options.get_safe("backend") != "cuda":
            self.output.warning(
                "RMM requires the CUDA backend to be enabled in Thrust by setting thrust/*:backend=cuda."
            )

    def _write_version_header(self):
        # Workaround for the `rapids_cmake_write_version_file(include/rmm/version_config.hpp)` CMakeLists.txt step
        # https://github.com/rapidsai/rapids-cmake/blob/branch-23.08/rapids-cmake/cmake/write_version_file.cmake
        # https://github.com/rapidsai/rapids-cmake/blob/branch-23.08/rapids-cmake/cmake/template/version.hpp.in
        major, minor, patch = self.version.split(".")[:3]
        save(self, os.path.join(self.source_folder, "include", "rmm", "version_config.hpp"),
            textwrap.dedent(f"""\
            #pragma once
            #define RMM_VERSION_MAJOR {int(major)}
            #define RMM_VERSION_MINOR {int(minor)}
            #define RMM_VERSION_PATCH {int(patch)}
            """)
        )

    def _patch_sources(self):
        if Version(self.version) < "23.08":
            # https://github.com/rapidsai/rmm/pull/1295
            # Add missing include in logger.hpp
            replace_in_file(self, os.path.join(self.source_folder, "include", "rmm", "logger.hpp"),
                            "#include <string>", "#include <string>\n#include <array>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._write_version_header()
        self._patch_sources()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        for pattern in ["*.hpp", "*.h"]:
            copy(self, pattern,
                 dst=os.path.join(self.package_folder, "include"),
                 src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")
