import os
import textwrap
from pathlib import Path

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import export_conandata_patches, get, copy
from conan.tools.layout import basic_layout

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

    @property
    def _min_cppstd(self):
        return 17

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def configure(self):
        # Thrust needs to use CUDA as the backend for RMM.
        # Disabled for ConanCenter CI.
        # self.options["thrust"].backend = "cuda"
        pass

    def requirements(self):
        self.requires("thrust/1.17.2")
        self.requires("spdlog/1.11.0")
        self.requires("fmt/9.1.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def _write_version_header(self):
        major, minor, patch = self.version.split(".")[:3]
        header_path = Path(self.source_folder) / "include" / "rmm" / "version_config.hpp"
        header_path.parent.mkdir(parents=True, exist_ok=True)
        header_path.write_text(textwrap.dedent(f"""\
            #pragma once
            #define RMM_VERSION_MAJOR {int(major)}
            #define RMM_VERSION_MINOR {int(minor)}
            #define RMM_VERSION_PATCH {int(patch)}
            """))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._write_version_header()

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        for pattern in ["*.hpp", "*.h"]:
            copy(
                self,
                pattern=pattern,
                dst=os.path.join(self.package_folder, "include"),
                src=os.path.join(self.source_folder, "include"),
            )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")
