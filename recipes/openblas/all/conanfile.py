from conans import ConanFile, CMake, tools
import os


class OpenblasConan(ConanFile):
    name = "openblas"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openblas.net"
    description = "An optimized BLAS library based on GotoBLAS2 1.13 BSD version"
    topics = (
        "openblas",
        "blas",
        "lapack"
    )
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_lapack": [True, False],
        "use_thread": [True, False],
        "dynamic_arch": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_lapack": False,
        "use_thread": True,
        "dynamic_arch": False
    }
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    _cmake = None
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('OpenBLAS-{}'.format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.options.build_lapack:
            self.output.warn("Building with lapack support requires a Fortran compiler.")

        self._cmake.definitions["NOFORTRAN"] = not self.options.build_lapack
        self._cmake.definitions["BUILD_WITHOUT_LAPACK"] = not self.options.build_lapack
        self._cmake.definitions["DYNAMIC_ARCH"] = self.options.dynamic_arch
        self._cmake.definitions["USE_THREAD"] = self.options.use_thread

        # Required for safe concurrent calls to OpenBLAS routines
        self._cmake.definitions["USE_LOCKING"] = not self.options.use_thread

        self._cmake.definitions["MSVC_STATIC_CRT"] = False # don't, may lie to consumer, /MD or /MT is managed by conan

        # This is a workaround to add the libm dependency on linux,
        # which is required to successfully compile on older gcc versions.
        self._cmake.definitions["ANDROID"] = self.settings.os in ["Linux", "Android"]

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.env_info.OpenBLAS_HOME = self.package_folder
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            if self.options.use_thread:
                self.cpp_info.system_libs.append("pthread")
            if self.options.build_lapack:
                self.cpp_info.system_libs.append("gfortran")
        self.cpp_info.names["cmake_find_package"] = "OpenBLAS"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenBLAS"
        self.cpp_info.names['pkg_config'] = "OpenBLAS"
