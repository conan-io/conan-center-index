import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, apply_conandata_patches, export_conandata_patches

required_conan_version = ">=2.1"


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
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ENKITS_INSTALL"] = True
        tc.cache_variables["ENKITS_BUILD_EXAMPLES"] = False
        tc.cache_variables["ENKITS_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
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
