from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.31.0"


class ErkirConan(ConanFile):
    name = "erkir"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/vahancho/erkir"
    license = "MIT"
    description = "a C++ library for geodetic and trigonometric calculations"
    topics = ("earth", "geodesy", "geography", "coordinate-systems", "geodetic", "datum")
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("*", src=os.path.join(self._source_subfolder, "include"), dst=os.path.join("include", "erkir"))
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.dylib*", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
