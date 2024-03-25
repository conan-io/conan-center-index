import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir

required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "minhook"
    description = "The Minimalistic x86/x64 API Hooking Library for Windows"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/TsudaKageyu/minhook"
    topics = ("hook", "windows")
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
        # minhook is a plain C projects
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} can only be built on Windows.")

        if self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration(f"{self.ref} can only be built on x86 or x86_64 architectures.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "minhook"))

    def package_info(self):
        if self.settings.arch == "x86_64":
            postfix = ".x64d" if self.settings.build_type == "Debug" else ".x64"
        else:
            postfix = ".x32d" if self.settings.build_type == "Debug" else ".x32"

        self.cpp_info.libs = [f"minhook{postfix}"]
        self.cpp_info.set_property("cmake_file_name", "minhook")
        self.cpp_info.set_property("cmake_target_name", "minhook::minhook")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "minhook"
        self.cpp_info.filenames["cmake_find_package_multi"] = "minhook"
        self.cpp_info.names["cmake_find_package"] = "minhook"
        self.cpp_info.names["cmake_find_package_multi"] = "minhook"
