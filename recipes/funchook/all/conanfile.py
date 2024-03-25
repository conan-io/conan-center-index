import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "funchook"
    description = "Hook function calls by inserting jump instructions at runtime"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kubo/funchook"
    topics = ("hook", "windows", "linux")
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

        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("capstone/4.0.2")

    def validate(self):
        if self.settings.os not in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built on {self.settings.os}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FUNCHOOK_BUILD_STATIC"] = not self.options.shared
        tc.variables["FUNCHOOK_BUILD_SHARED"] = self.options.shared
        tc.variables["FUNCHOOK_BUILD_TESTS"] = False
        tc.variables["FUNCHOOK_INSTALL"] = True
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        if is_msvc(self) and self.options.shared:
            self.cpp_info.libs = ["funchook_dll"]
        else:
            self.cpp_info.libs = ["funchook"]

        self.cpp_info.set_property("cmake_file_name", "funchook")
        self.cpp_info.set_property("cmake_target_name", "funchook::funchook")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("psapi")
        else:
            self.cpp_info.system_libs.append("dl")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "funchook"
        self.cpp_info.filenames["cmake_find_package_multi"] = "funchook"
        self.cpp_info.names["cmake_find_package"] = "funchook"
        self.cpp_info.names["cmake_find_package_multi"] = "funchook"
