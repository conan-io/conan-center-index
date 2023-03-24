import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, load, save, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version


required_conan_version = ">=1.54.0"


class SoxrConan(ConanFile):
    name = "soxr"
    description = "The SoX Resampler library libsoxr performs fast, high-quality one-dimensional sample rate conversion."
    homepage = "https://sourceforge.net/projects/soxr/"
    topics = ("resampling", "audio", "sample-rate", "conversion")
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openmp": [True, False],
        "with_lsr_bindings": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openmp": False,
        "with_lsr_bindings": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

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
        if Version(self.version) < "3.21":
            # silence warning
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0115"] = "OLD"
        if is_msvc(self):
            tc.variables["BUILD_SHARED_RUNTIME"] = not is_msvc_static_runtime(self)
        # Disable SIMD based resample engines for Apple Silicon and iOS ARMv8 architecture
        if (self.settings.os == "Macos" or self.settings.os == "iOS") and self.settings.arch == "armv8":
            tc.variables["WITH_CR32S"] = False
            tc.variables["WITH_CR64S"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["WITH_OPENMP"] = self.options.with_openmp
        tc.variables["WITH_LSR_BINDINGS"] = self.options.with_lsr_bindings
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _extract_pffft_license(self):
        pffft_c = load(self, os.path.join(self.source_folder, "src", "pffft.c"))
        return pffft_c[pffft_c.find("/* Copyright")+3:pffft_c.find("modern CPUs.")+13]

    def package(self):
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENCE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE_pffft"), self._extract_pffft_license())
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "doc"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        # core component
        self.cpp_info.components["core"].set_property("pkg_config_name", "soxr")
        self.cpp_info.components["core"].libs = ["soxr"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["core"].system_libs = ["m"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["core"].defines.append("SOXR_DLL")
        if not self.options.shared and self.options.with_openmp:
            if is_msvc(self):
                openmp_flags = ["-openmp"]
            elif self.settings.compiler in ("gcc", "clang"):
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler == "apple-clang":
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]
            else:
                openmp_flags = []
            self.cpp_info.components["core"].exelinkflags = openmp_flags
            self.cpp_info.components["core"].sharedlinkflags = openmp_flags
        # lsr component
        if self.options.with_lsr_bindings:
            self.cpp_info.components["lsr"].set_property("pkg_config_name", "soxr-lsr")
            self.cpp_info.components["lsr"].libs = ["soxr-lsr"]
            if self.settings.os == "Windows" and self.options.shared:
                self.cpp_info.components["lsr"].defines.append("SOXR_DLL")
            self.cpp_info.components["lsr"].requires = ["core"]
