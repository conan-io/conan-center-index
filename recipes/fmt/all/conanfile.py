from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os


class FmtConan(ConanFile):
    name = "fmt"
    homepage = "https://github.com/fmtlib/fmt"
    description = "A safe and fast alternative to printf and IOStreams."
    topics = ("conan", "fmt", "format", "iostream", "printf")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    exports_sources = ['CMakeLists.txt']
    generators = 'cmake'
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "header_only": [True, False], "fPIC": [True, False], "with_fmt_alias": [True, False]}
    default_options = {"shared": False, "header_only": False, "fPIC": True, "with_fmt_alias": False}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            self.settings.clear()
            del self.options.fPIC
            del self.options.shared
        elif self.version == "6.1.0" and \
             self.settings.os == "Windows" and \
             self.settings.compiler == "Visual Studio" and \
             Version(self.settings.compiler.version) < "16" and \
             self.options.shared:
            raise ConanInvalidConfiguration("Could not support this specific configuration. "
                                            "Try static or header-only instead.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["FMT_DOC"] = False
        cmake.definitions["FMT_TEST"] = False
        cmake.definitions["FMT_INSTALL"] = True
        cmake.definitions["FMT_LIB_DIR"] = "lib"
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        if not self.options.header_only:
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy("LICENSE.rst", dst="licenses", src=self._source_subfolder)
        if self.options.header_only:
            src_dir = os.path.join(self._source_subfolder, "src")
            header_dir = os.path.join(self._source_subfolder, "include")
            dst_dir = os.path.join("include", "fmt")
            self.copy("*.h", dst="include", src=header_dir)
            self.copy("*.cc", dst=dst_dir, src=src_dir)
        else:
            cmake = self._configure_cmake()
            cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    def package_info(self):
        if self.options.with_fmt_alias:
            self.cpp_info.defines.append("FMT_STRING_ALIAS=1")
        if self.options.header_only:
            self.cpp_info.defines = ["FMT_HEADER_ONLY"]
        else:
            self.cpp_info.libs = tools.collect_libs(self)
            if self.options.shared:
                self.cpp_info.defines.append('FMT_SHARED')
                self.cpp_info.bindirs.append("lib")
