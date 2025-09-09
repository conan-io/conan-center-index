from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.build import check_min_cppstd


import os


class Librdtsc(ConanFile):
    name = "librdtsc"
    description = "A simple multi-platform library for reading TSC values on x86-64 and ARM architectures"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gabrieleara/librdtsc"
    topics = ("librdtsc", "cpu")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
            "shared": [True, False],
            "fPIC": [True, False],
            "use_hpet": [True, False],
            "use_pmu": [True, False],
            }
    default_options = {
            "shared": False,
            "fPIC": True,
            "use_hpet": False,
            "use_pmu": False,
            }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBRDTSC_OS_LINUX"] = str(self.settings.os) == "Linux"
        arch = str(self.settings.arch)
        tc.variables["LIBRDTSC_ARCH_X86"] = arch in ("x86", "x86_64")
        tc.variables["LIBRDTSC_ARCH_ARM"] = arch == "armv7"
        tc.variables["LIBRDTSC_ARCH_ARM64"] = arch == "armv8"
        tc.variables["LIBRDTSC_USE_HPET"] = self.options.use_hpet
        tc.variables["LIBRDTSC_USE_PMU"] = self.options.use_pmu
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["rdtsc"]

