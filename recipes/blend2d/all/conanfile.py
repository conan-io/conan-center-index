import os

from conan import ConanFile
from conan import tools
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.scm import Version
from conan.tools.files import apply_conandata_patches
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.50.0"

class Blend2dConan(ConanFile):
    name = "blend2d"
    description = "2D Vector Graphics Engine Powered by a JIT Compiler"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://blend2d.com/"
    topics = ("2d-graphics", "rasterization", "asmjit", "jit")
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
        tools.files.copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder='src')

    def requirements(self):
        self.requires("asmjit/cci.20220210")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

        # In Visual Studio < 16, there are compilation error. patch is already provided.
        # https://github.com/blend2d/blend2d/commit/63db360c7eb2c1c3ca9cd92a867dbb23dc95ca7d
        if is_msvc(self) and tools.Version(self.settings.compiler.version) < "16":
            raise ConanInvalidConfiguration("This recipe does not support this compiler version")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["BUILD_TESTING"] = False
        toolchain.variables["BLEND2D_TEST"] = False
        toolchain.variables["BLEND2D_EMBED"] = False
        toolchain.variables["BLEND2D_STATIC"] = not self.options.shared
        toolchain.variables["BLEND2D_NO_STDCXX"] = False
        if not self.options.shared:
            toolchain.variables["CMAKE_C_FLAGS"] = "-DBL_STATIC"
            toolchain.variables["CMAKE_CXX_FLAGS"] = "-DBL_STATIC"
        toolchain.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        tools.files.copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["blend2d"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "rt",])
        if not self.options.shared:
            self.cpp_info.defines.append("BL_STATIC")
