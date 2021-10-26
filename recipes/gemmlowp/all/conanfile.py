import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


required_conan_version = ">=1.37.0"

class GemmlowpConan(ConanFile):
    name = "gemmlowp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/gemmlowp"
    description = "Low-precision matrix multiplication"
    topics = ("gemm", "matrix")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("shared is not supported on Windows")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions['BUILD_TESTING'] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["eight_bit_int_gemm"].includedirs.append(os.path.join("include", "gemmlowp"))
        self.cpp_info.components["eight_bit_int_gemm"].names["cmake_find_package"] = "eight_bit_int_gemm"
        self.cpp_info.components["eight_bit_int_gemm"].names["cmake_find_package_multi"] = "eight_bit_int_gemm"
        self.cpp_info.components["eight_bit_int_gemm"].libs = ["eight_bit_int_gemm"]
        if self.settings.os == "Linux":
            self.cpp_info.components["eight_bit_int_gemm"].system_libs.extend(["pthread"])
