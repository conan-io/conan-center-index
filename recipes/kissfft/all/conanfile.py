import os
from conans import ConanFile, CMake, tools


class KissfftConan(ConanFile):
    name = "kissfft"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mborgerding/kissfft"
    description = "a Fast Fourier Transform (FFT) library that tries to Keep it Simple, Stupid"
    topics = ("conan",)
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "datatype": ["float", "double", "int16_t", "int32_t", "SIMD"],
               "use_alloca": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "datatype": "float",
                       "use_alloca": False}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake",

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "_build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["KISSFFT_PKGCONFIG"] = False
        cmake.definitions["KISSFFT_STATIC"] = not self.options.shared
        cmake.definitions["KISSFFT_TEST"] = False
        cmake.definitions["KISSFFT_TOOLS"] = False
        cmake.definitions["KISSFFT_DATATYPE"] = self.options.datatype
        cmake.definitions["KISSFFT_USE_ALLOCA"] = self.options.use_alloca
        cmake.configure()
        return cmake

    def build(self):
        # Cannot extract major (ABI) version from Makefile
        # no idea why doesn't it work on CCI?
        major, minor, patch = self.version.split(".")
        makefile = "KFVER_MAJOR = %s\n" % major
        makefile += "KFVER_MINOR = %s\n" % minor
        makefile += "KFVER_PATCH = %s\n" % patch
        # debug!
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "file(READ Makefile _MAKEFILE_CONTENTS)",
                              'file(READ Makefile _MAKEFILE_CONTENTS)\n'
                              'message(STATUS "_MAKEFILE_CONTENTS ${_MAKEFILE_CONTENTS}")')
        tools.save(os.path.join(self._source_subfolder, "Makefile"), makefile)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["kissfft-%s" % self.options.datatype]
        if self.options.shared:
            self.cpp_info.defines.append("KISS_FFT_SHARED")
