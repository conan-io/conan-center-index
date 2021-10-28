from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class FmtConan(ConanFile):
    name = "fmt"
    homepage = "https://github.com/fmtlib/fmt"
    description = "A safe and fast alternative to printf and IOStreams."
    topics = ("conan", "fmt", "format", "iostream", "printf")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "header_only": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],
        "with_fmt_alias": [True, False],
        "with_os_api": [True, False],
    }
    default_options = {
        "header_only": False,
        "shared": False,
        "fPIC": True,
        "with_fmt_alias": False,
        "with_os_api": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _has_with_os_api_option(self):
        return tools.Version(self.version) >= "7.0.0"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_with_os_api_option:
            del self.options.with_os_api

    def configure(self):
        if self.options.header_only:
            del self.options.fPIC
            del self.options.shared
            del self.options.with_os_api
        elif self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.options.get_safe("shared") and self.settings.compiler == "Visual Studio" and \
           "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Visual Studio build for shared library with MT runtime is not supported")

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()
        else:
            del self.info.options.with_fmt_alias

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FMT_DOC"] = False
        self._cmake.definitions["FMT_TEST"] = False
        self._cmake.definitions["FMT_INSTALL"] = True
        self._cmake.definitions["FMT_LIB_DIR"] = "lib"
        if self._has_with_os_api_option:
            self._cmake.definitions["FMT_OS"] = self.options.with_os_api
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if not self.options.header_only:
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy("LICENSE.rst", dst="licenses", src=self._source_subfolder)
        if self.options.header_only:
            self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        else:
            cmake = self._configure_cmake()
            cmake.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "fmt"
        self.cpp_info.names["cmake_find_package_multi"] = "fmt"
        self.cpp_info.names["pkg_config"] = "fmt"
        if self.options.header_only:
            self.cpp_info.components["fmt-header-only"].defines.append("FMT_HEADER_ONLY=1")
            if self.options.with_fmt_alias:
                self.cpp_info.components["fmt-header-only"].defines.append("FMT_STRING_ALIAS=1")
        else:
            postfix = "d" if self.settings.build_type == "Debug" else ""
            self.cpp_info.libs = ["fmt" + postfix]
            if self.options.with_fmt_alias:
                self.cpp_info.defines.append("FMT_STRING_ALIAS=1")
            if self.options.shared:
                self.cpp_info.defines.append("FMT_SHARED")
