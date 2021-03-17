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
               "datatype": ["float", "double", "int16_t", "int32_t", "simd"],
               "use_alloca": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "datatype": "float",
                       "use_alloca": False}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake",
    _cmake = None

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
        if self._cmake:
            return self._cmake
        cmake = CMake(self)
        cmake.definitions["KISSFFT_PKGCONFIG"] = False
        cmake.definitions["KISSFFT_STATIC"] = not self.options.shared
        cmake.definitions["KISSFFT_TEST"] = False
        cmake.definitions["KISSFFT_TOOLS"] = False
        cmake.definitions["KISSFFT_DATATYPE"] = self.options.datatype
        cmake.definitions["KISSFFT_USE_ALLOCA"] = self.options.use_alloca
        cmake.configure()
        self._cmake = cmake
        return self._cmake

    def build(self):
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
