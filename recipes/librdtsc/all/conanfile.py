from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy

import os


class Librdtsc(ConanFile):
    name = "librdtsc"
    version = "v0.3"
    description = "A simple multi-platform library for reading TSC values on x86-64 and ARM architectures"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gabrieleara/librdtsc.git"
    topics = ("librdtsc", "cpu")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
            "shared": [True, False],
            "fPIC": [True, False],
            "use_hpet": [True, False],
            "use_pmu": [True, False],
            "arch": ["x86", "arm", "arm64"]
            }
    default_options = {
            "shared": False,
            "fPIC": True,
            "use_hpet": False,
            "use_pmu": False,
            "arch": "x86"
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
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBRDTSC_OS_LINUX"] = True
        tc.variables["LIBRDTSC_ARCH_X86"] = self.options.arch == "x86"
        tc.variables["LIBRDTSC_ARCH_ARM"] = self.options.arch == "arm"
        tc.variables["LIBRDTSC_ARCH_ARM64"] = self.options.arch == "arm64"
        tc.variables["LIBRDTSC_USE_HPET"] = self.options.use_hpet
        tc.variables["LIBRDTSC_USE_PMU"] = self.options.use_pmu
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "librdtsc")
        self.cpp_info.set_property("cmake_target_name", "librdtsc::librdtsc")
        self.cpp_info.libs = ["rdtsc"]

