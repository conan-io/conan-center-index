from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=1.50.0"


class AsmjitConan(ConanFile):
    name = "asmjit"
    description = "AsmJit is a lightweight library for machine code " \
                  "generation written in C++ language."
    license = "Zlib"
    topics = ("asmjit", "compiler", "assembler", "jit")
    homepage = "https://asmjit.com"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ASMJIT_EMBED"] = False
        tc.variables["ASMJIT_STATIC"] = not self.options.shared
        if self.version == "cci.20210306":
            tc.variables["ASMJIT_BUILD_X86"] = self.settings.os in ["x86", "x86_64"]
        tc.variables["ASMJIT_TEST"] = False
        tc.variables["ASMJIT_NO_NATVIS"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "asmjit")
        self.cpp_info.set_property("cmake_target_name", "asmjit::asmjit")

        self.cpp_info.names["cmake_find_package"] = "asmjit"
        self.cpp_info.names["cmake_find_package_multi"] = "asmjit"

        self.cpp_info.libs = ["asmjit"]
        if not self.options.shared:
            self.cpp_info.defines = ["ASMJIT_STATIC"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "rt"]
