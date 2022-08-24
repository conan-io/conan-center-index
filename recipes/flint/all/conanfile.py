import os

from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.33.0"


class FlintConan(ConanFile):
    name = "flint"
    description = "FLINT (Fast Library for Number Theory)"
    license = "LGPL-2.1-or-later"
    topics = ("math", "numerical")
    homepage = "https://www.flintlib.org"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

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

    def requirements(self):
        self.requires("gmp/6.2.1")
        self.requires("mpfr/4.1.0")
        if self.settings.compiler == "Visual Studio":
            self.requires("pthreads4w/3.0.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_DOCS"] = False
        self._cmake.definitions["WITH_NTL"] = False
        # IPO/LTO breaks clang builds
        self._cmake.definitions["IPO_SUPPORTED"] = False
        # No BLAS yet
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_CBLAS"] = True
        # handle run in a cross-build
        if tools.cross_building(self):
            self._cmake.definitions["FLINT_USES_POPCNT_EXITCODE"] = "1"
            self._cmake.definitions["FLINT_USES_POPCNT_EXITCODE__TRYRUN_OUTPUT"] = ""
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "libflint"
        self.cpp_info.names["cmake_find_package_multi"] = "libflint"

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "m"]

        self.cpp_info.includedirs.append(os.path.join("include", "flint"))
        self.cpp_info.libs = tools.collect_libs(self)
