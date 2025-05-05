from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.files import copy, get, apply_conandata_patches, export_conandata_patches
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=1.52.0"


class PicobenchConan(ConanFile):
    name = "picobench"
    description = "A micro microbenchmarking library for C++11 in a single header file"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/iboB/picobench"
    topics = ("benchmark", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_cli": [True, False],
    }
    default_options = {
        "with_cli": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.with_cli:
            del self.info.settings.compiler
        else:
            self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PICOBENCH_BUILD_TOOLS"] = self.options.with_cli
        tc.variables["PICOBENCH_BUILD_TESTS"] = False
        tc.variables["PICOBENCH_BUILD_EXAMPLES"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.install()

    def package_info(self):
        if self.options.with_cli:
            # TODO: Legacy, to be removed on Conan 2.0
            binpath = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var: {}".format(binpath))
            self.env_info.PATH.append(binpath)
        else:
            self.cpp_info.bindirs = []

        self.cpp_info.libdirs = []
