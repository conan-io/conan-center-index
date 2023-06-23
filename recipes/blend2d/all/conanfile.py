from conan import ConanFile
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
from conan.tools.microsoft import check_min_vs
import os

required_conan_version = ">=1.53.0"


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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("asmjit/cci.20230325")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

        if Version(self.version) < "0.8":
            # In Visual Studio < 16, there are compilation error. patch is already provided.
            # https://github.com/blend2d/blend2d/commit/63db360c7eb2c1c3ca9cd92a867dbb23dc95ca7d
            check_min_vs(self, 192)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BLEND2D_TEST"] = False
        tc.variables["BLEND2D_EMBED"] = False
        tc.variables["BLEND2D_STATIC"] = not self.options.shared
        tc.variables["BLEND2D_NO_STDCXX"] = False
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        if not valid_min_cppstd(self, 11):
            tc.variables["CMAKE_CXX_STANDARD"] = 11
        if not self.options.shared:
            tc.preprocessor_definitions["BL_STATIC"] = "1"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
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
            self.cpp_info.system_libs.extend(["pthread", "rt",])
        if not self.options.shared:
            self.cpp_info.defines.append("BL_STATIC")
