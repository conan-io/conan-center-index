from conans import ConanFile, tools, CMake
import os


class HttpParserConan(ConanFile):
    name = "http_parser"
    description = "http request/response parser for c "
    topics = ("conan", "http", "parser")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nodejs/http-parser"
    license = ("MIT",)
    exports_sources = "CMakeLists.txt",
    generators = "cmake",
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],

    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows" or self.options.shared:
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "http-parser-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _get_cmake(self):
        cmake = CMake(self)
        return cmake

    def build(self):
        cmake = self._get_cmake()
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE-MIT", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        cmake = self._get_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["http_parser"]
