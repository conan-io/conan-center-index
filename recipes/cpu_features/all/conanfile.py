import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class CpuFeaturesConan(ConanFile):
    name = "cpu_features"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/cpu_features"
    description = "A cross platform C99 library to get cpu features at runtime."
    topics = ("conan", "cpu", "features", "cpuid")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_PIC"] = self.options.get_safe("fPIC", True)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake(build_folder=self._build_subfolder)
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CpuFeatures"
        self.cpp_info.names["cmake_find_package_multi"] = "CpuFeatures"
        self.cpp_info.components["libcpu_features"].names["cmake_find_package"] = "cpu_features"
        self.cpp_info.components["libcpu_features"].names["cmake_find_package_multi"] = "cpu_features"
        self.cpp_info.components["libcpu_features"].libs = ["cpu_features"]
        self.cpp_info.components["libcpu_features"].includedirs = [os.path.join("include", "cpu_features")]
        if self.settings.os == "Linux":
            self.cpp_info.components["libcpu_features"].system_libs = ["dl"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
