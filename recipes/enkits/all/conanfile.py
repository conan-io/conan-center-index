import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, export_conandata_patches, get, replace_in_file

required_conan_version = ">=1.53.0"


class EnkiTSConan(ConanFile):
    name = "enkits"
    description = "A permissively licensed C and C++ Task Scheduler for creating parallel programs."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dougbinks/enkiTS"
    topics = ("c", "thread", "multithreading", "scheduling", "gamedev")

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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENKITS_INSTALL"] = True
        tc.variables["ENKITS_BUILD_EXAMPLES"] = False
        tc.variables["ENKITS_BUILD_SHARED"] = self.options.shared
        tc.generate()

    def _patch_sources(self):
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            'install(TARGETS enkiTS DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/enkiTS")',
            "install(TARGETS enkiTS ARCHIVE LIBRARY RUNTIME)",
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "License.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["enkiTS"]

        if self.options.shared:
            self.cpp_info.defines.append("ENKITS_DLL=1")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
