from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class YyjsonConan(ConanFile):
    name = "yyjson"
    description = "A high performance JSON library written in ANSI C."
    license = "MIT"
    topics = ("yyjson", "json", "serialization", "deserialization")
    homepage = "https://github.com/ibireme/yyjson"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "yyjson"
        self.cpp_info.names["cmake_find_package_multi"] = "yyjson"
        self.cpp_info.libs = ["yyjson"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("YYJSON_IMPORTS")
