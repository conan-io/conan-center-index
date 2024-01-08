from conan import ConanFile
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"


class HwlocConan(ConanFile):
    name = "hwloc"
    description = "Portable Hardware Locality (hwloc)"
    topics = ("hardware", "topology")
    license = "BSD-3-Clause"
    homepage = "https://www.open-mpi.org/projects/hwloc/"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libxml2": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libxml2": False
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def requirements(self):
        if self.options.with_libxml2:
            self.requires("libxml2/2.11.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        if self.settings.os == "Windows":
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def generate(self):
        if self.settings.os == "Windows":
            deps = CMakeDeps(self)
            deps.generate()
            tc = CMakeToolchain(self)
            tc.cache_variables["HWLOC_ENABLE_TESTING"] = 'OFF'
            tc.cache_variables["HWLOC_SKIP_LSTOPO"] = 'ON'
            tc.cache_variables["HWLOC_SKIP_TOOLS"] = 'ON'
            tc.cache_variables["HWLOC_SKIP_INCLUDES"] = 'OFF'
            tc.cache_variables["HWLOC_WITH_OPENCL"] = 'OFF'
            tc.cache_variables["HWLOC_WITH_CUDA"] = 'OFF'
            tc.cache_variables["HWLOC_BUILD_SHARED_LIBS"] = self.options.shared
            tc.cache_variables["HWLOC_WITH_LIBXML2"] = self.options.with_libxml2
            tc.generate()
        else:
            deps = PkgConfigDeps(self)
            deps.generate()
            tc = AutotoolsToolchain(self)
            if not self.options.with_libxml2:
                tc.configure_args.extend(["--disable-libxml2"])
            tc.configure_args.extend(["--disable-io", "--disable-cairo"])
            tc.generate()

    def build(self):
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure(build_script_folder=os.path.join("contrib", "windows-cmake"))
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.install()
            # remove PDB files
            rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        else:
            autotools = Autotools(self)
            autotools.install()
            fix_apple_shared_install_name(self)
            # remove tools
            rmdir(self, os.path.join(self.package_folder, "bin"))

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "hwloc")
        self.cpp_info.libs = ["hwloc"]

        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs = ["m"]
        if is_apple_os(self):
            self.cpp_info.frameworks = ['IOKit', 'Foundation', 'CoreFoundation']
