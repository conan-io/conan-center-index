from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2"


class Blend2dConan(ConanFile):
    name = "blend2d"
    description = "2D Vector Graphics Engine Powered by a JIT Compiler"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://blend2d.com/"
    topics = ("2d-graphics", "rasterization", "asmjit", "jit")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_jit": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jit": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_jit:
            self.requires("asmjit/cci.20251209")

    def validate(self):
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BLEND2D_TEST"] = False
        tc.variables["BLEND2D_STATIC"] = not self.options.shared
        tc.variables["BLEND2D_NO_STDCXX"] = False
        tc.variables["BLEND2D_EXTERNAL_ASMJIT"] = True
        tc.variables["BLEND2D_NO_JIT"] = not self.options.with_jit
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "blend2d")
        self.cpp_info.set_property("cmake_target_name", "blend2d::blend2d")
        self.cpp_info.libs = ["blend2d"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "m"])
        if not self.options.shared:
            self.cpp_info.defines.append("BL_STATIC")
