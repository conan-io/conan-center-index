import os
from conan import ConanFile
from conan.errors import ConanException
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.1"


class mdnsdConan(ConanFile):
    name = "pro-mdnsd"
    description = "Improved version of Jeremie Miller's MDNS-SD implementation"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Pro/mdnsd"
    topics = ("dns", "daemon", "multicast", "embedded", "c")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "compile_as_cpp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "compile_as_cpp": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.compile_as_cpp:
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MDNSD_ENABLE_SANITIZERS"] = False
        tc.variables["MDNSD_COMPILE_AS_CXX"] = self.options.compile_as_cpp
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        if Version(self.version) > "0.8.4": # pylint: disable=conan-unreachable-upper-version
            raise ConanException("CMAKE_POLICY_VERSION_MINIMUM hardcoded to 3.5, check if new version supports CMake 4")

        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mdnsd")
        self.cpp_info.set_property("cmake_target_name", "libmdnsd")
        self.cpp_info.set_property("cmake_target_aliases", ["mdnsd::mdnsd"])
        self.cpp_info.libs = ["mdnsd"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "wsock32"]
