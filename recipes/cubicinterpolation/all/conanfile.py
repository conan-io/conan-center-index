from conans import ConanFile, CMake, tools
import glob
import os

class CubicInterpolationConan(ConanFile):
    name = "CubicInterpolation"
    homepage = "https://github.com/MaxSac/cubic_interpolation"
    license = "MIT"
    author = "Maximilian Sackel mail@maxsac.de"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Leightweight interpolation library based on boost and eigen."
    topics = ("interpolation", "splines", "cubic", "bicubic", "boost", "eigen3")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake_find_package"
    _source_folder = "source_folder"
    exports_sources = "*"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("cubic_interpolation-*/")[0]
        os.rename(extracted_dir, self._source_folder)

    def requirements(self):
        self.requires("boost/1.75.0")
        self.requires("eigen/3.3.9")

    def build(self):
        self.cmake = CMake(self)
        self.cmake.configure(source_folder=self._source_folder)
        self.cmake.build()

    def package(self):
        self.cmake.install()
        self.copy("license*", dst="licenses", ignore_case=True, keep_path=False)
        self.copy("*.h", dst="include", src=f"{self._source_folder}/src")
        self.copy("*.hpp", dst="include", src="{self._source_folder}/src")
        self.copy("*.h", dst="include")
        self.copy("*.hpp", dst="include")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.dylib*", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
