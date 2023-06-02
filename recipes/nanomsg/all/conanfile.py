from conan import ConanFile
from conan.tools.files import apply_conandata_patches,  get, copy, rm, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os


required_conan_version = ">=1.53.0"

class NanomsgConan(ConanFile):
    name = "nanomsg"
    description = "a socket library that provides several common communication patterns."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nanomsg/nanomsg"
    topics = ("socket", "protocols", "communication")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_coverage": [True, False],
        "enable_getaddrinfo_a":[True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_coverage": False,
        "enable_getaddrinfo_a":True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NN_STATIC_LIB"] = not self.options.shared
        tc.variables["NN_ENABLE_COVERAGE"] = self.options.enable_coverage
        tc.variables["NN_ENABLE_GETADDRINFO_A"] = self.options.enable_getaddrinfo_a
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["nanomsg"]
        self.cpp_info.set_property("cmake_file_name", "nanomsg")
        self.cpp_info.set_property("cmake_target_name", "nanomsg::nanomsg")

        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.system_libs.extend(["mswsock", "ws2_32", "advapi32"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("anl")
            self.cpp_info.system_libs.append("rt")
            self.cpp_info.system_libs.append("nsl")

        if not self.options.shared:
            self.cpp_info.defines.append("NN_STATIC_LIB")
        if self.options.enable_coverage:
            self.cpp_info.defines.append("NN_ENABLE_COVERAGE")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "nanomsg"
        self.cpp_info.names["cmake_find_package_multi"] = "nanomsg"
