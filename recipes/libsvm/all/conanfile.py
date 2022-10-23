from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy

import os

required_conan_version = ">=1.52.0"

class libsvmConan(ConanFile):
    name = "libsvm"
    description = "Libsvm is a simple, easy-to-use, and efficient software for SVM classification and regression"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.csie.ntu.edu.tw/~cjlin/libsvm/"
    license = "BSD-3-Clause"
    topics = "svm", "vector"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
        }
    default_options = {
        "shared": False,
        "fPIC": True
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if (
            self.settings.compiler == "Visual Studio" and
            "MT" in self.settings.compiler.runtime and
            self.options.shared
        ):
            raise ConanInvalidConfiguration(
                f"{self.name} can not be built as shared library + runtime {self.settings.compiler.runtime}."
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBSVM_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "COPYRIGHT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["svm"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
