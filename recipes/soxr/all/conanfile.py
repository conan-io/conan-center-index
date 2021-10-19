import itertools
import os
from conans import ConanFile, CMake, tools


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
    exports_sources = "patches/**"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake        
        self._cmake = CMake(self)
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["BUILD_SHARED_RUNTIME"] = "MD" in self.settings.compiler.runtime
        elif self.settings.compiler == "msvc":
            self._cmake.definitions["BUILD_SHARED_RUNTIME"] = self.settings.compiler.runtime == "dynamic"
        self._cmake.definitions["BUILD_TESTS"] = False   
        self._cmake.definitions["WITH_OPENMP"] = self.options.with_openmp
        self._cmake.definitions["WITH_LSR_BINDINGS"] = self.options.with_lsr_bindings
        self._cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_pffft_license(self):
        # extract license header from pffft.c and store it in the package folder
        with open(os.path.join(self._source_subfolder, "src", "pffft.c"), "r") as f:
            # the license header starts in line 3 and ends in line 55
            lines = map(lambda line: line.lstrip("/* "), itertools.islice(f, 3, 55))
            with open(os.path.join(self.package_folder, "licenses", "pffft"), "w") as f2:
                f2.writelines(lines)

    def package(self):
        self.copy("LICENCE", dst="licenses", src=self._source_subfolder)
        self._extract_pffft_license()
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "doc"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["soxr"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["m"]
        if not self.options.shared and self.options.with_openmp:
            if self.settings.compiler in ("Visual Studio", "msvc"):
                openmp_flags = ["/openmp"]
            elif self.settings.compiler in ("gcc", "clang"):
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler == "apple-clang":
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]
            else:
                openmp_flags = []
            self.cpp_info.cxxflags = openmp_flags
            self.cpp_info.sharedlinkflags = openmp_flags
