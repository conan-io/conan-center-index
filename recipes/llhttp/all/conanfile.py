from conan import ConanFile, tools
from conans import CMake
from conan.tools.files import patch
import os

required_conan_version = ">=1.43.0"


class LlhttpParserConan(ConanFile):
    name = "llhttp"
    description = "http request/response parser for c "
    topics = ("http", "parser")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nodejs/llhttp"
    license = ("MIT",)
    generators = ("cmake",)
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    exports_sources = "CMakeLists.txt", "patches/*"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def source(self):
        tools.files.get(self, 
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            strip_root=True,
        )

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(
            "LICENSE-MIT",
            src=os.path.join(self.source_folder, self._source_subfolder),
            dst="licenses",
        )
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "llhttp")
        self.cpp_info.set_property("cmake_target_name", "llhttp::llhttp")
        self.cpp_info.set_property("pkg_config_name", "libllhttp")
        self.cpp_info.libs = ["llhttp"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "llhttp"
        self.cpp_info.names["cmake_find_package_multi"] = "llhttp"
        self.cpp_info.names["pkg_config"] = "libllhttp"
