from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import copy, download, export_conandata_patches, get, patch, rm
import os

required_conan_version = ">=1.54.0"

class ZxcvbnConan(ConanFile):
    name = "zxcvbn"
    description = "C/C++ implementation of the zxcvbn password strength estimation"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tsyrogit/zxcvbn-c"
    topics = ("password", "security", "zxcvbn")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def build_requirements(self):
        if cross_building(self):
            self.tool_requires(f"{self.name}/{self.version}")

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def source(self):
        sources = self.conan_data["sources"][self.version]
        get(self, **sources["archive"], strip_root=True)
        download(self, filename="CMakeLists.txt", **sources["cmakelists"])
        # fixes Linux build when "Makefile" is generated but the original "makefile" used
        rm(self, "makefile", self.source_folder)
        # for the conditional #include "stdafx.h" in zxcvbn.c
        with open(os.path.join(self.source_folder, "stdafx.h"), "ab") as f:
            f.close()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def _patch_sources(self):
        for it in self.conan_data.get("patches", {}).get(self.version, []):
            if "windows" in it["patch_file"] and self.settings.os not in ["Windows", "Emscripten"]:
                continue
            if "crossbuilding" in it["patch_file"] and not cross_building(self):
                continue
            entry = it.copy()
            patch_file_path = os.path.join(self.export_sources_folder, entry.pop("patch_file"))
            patch(self, patch_file=patch_file_path, **entry)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="zxcvbn-shared" if self.options.shared else "zxcvbn-static")

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "zxcvbn.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        for pattern in ["*.a", "*.so*", "*.dylib", "*.lib"]:
            copy(self, pattern, src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        for pattern in ["*.dll", "dictgen", "dictgen.exe"]:
            copy(self, pattern, src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["zxcvbn"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
