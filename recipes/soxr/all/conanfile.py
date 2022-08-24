import functools
import os
from conan import ConanFile, tools
from conans import CMake
from conan.tools.microsoft import msvc_runtime_flag, is_msvc


required_conan_version = ">=1.45.0"


class SoxrConan(ConanFile):
    name = "soxr"
    description = "The SoX Resampler library libsoxr performs fast, high-quality one-dimensional sample rate conversion."
    homepage = "https://sourceforge.net/projects/soxr/"
    topics = ("resampling", "audio", "sample-rate", "conversion")
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openmp": [True, False],
        "with_lsr_bindings": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openmp": False,
        "with_lsr_bindings": True
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        if is_msvc(self):
            cmake.definitions["BUILD_SHARED_RUNTIME"] = msvc_runtime_flag(self) == "MD"
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["WITH_OPENMP"] = self.options.with_openmp
        cmake.definitions["WITH_LSR_BINDINGS"] = self.options.with_lsr_bindings
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_pffft_license(self):
        pffft_c = tools.load(os.path.join(self._source_subfolder, "src", "pffft.c"))
        license_contents = pffft_c[pffft_c.find("/* Copyright")+3:pffft_c.find("modern CPUs.")+13]
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package(self):
        self.copy("LICENCE", dst="licenses", src=self._source_subfolder)
        self._extract_pffft_license()
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "doc"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        # core component
        self.cpp_info.components["core"].names["pkg_config"] = "soxr"
        self.cpp_info.components["core"].libs = ["soxr"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["core"].system_libs = ["m"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["core"].defines.append("SOXR_DLL")
        if not self.options.shared and self.options.with_openmp:
            if self.settings.compiler in ("Visual Studio", "msvc"):
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
            self.cpp_info.components["lsr"].names["pkg_config"] = "soxr-lsr"
            self.cpp_info.components["lsr"].libs = ["soxr-lsr"]
            if self.settings.os == "Windows" and self.options.shared:
                self.cpp_info.components["lsr"].defines.append("SOXR_DLL")
            self.cpp_info.components["lsr"].requires = ["core"]
