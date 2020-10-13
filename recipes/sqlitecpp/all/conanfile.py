from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration
import os


class SQLiteCppConan(ConanFile):
    name = "sqlitecpp"
    description = "SQLiteCpp is a smart and easy to use C++ sqlite3 wrapper"
    topics = ("conan", "sqlitecpp", "sqlite3")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/SRombauts/SQLiteCpp"
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "lint": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "lint": False
                       }
    requires = ("sqlite3/3.32.3")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_mingw_windows(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'gcc'

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("SQLiteCpp can not be built as shared lib on Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "SQLiteCpp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_clang(self):
        if self.settings.compiler == "clang" and \
           Version(self.settings.compiler.version) < "6.0" and \
           self.settings.compiler.libcxx == "libc++" and \
           Version(self.version) < "3":
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "include", "SQLiteCpp", "Utils.h"),
                "const nullptr_t nullptr = {};",
                "")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SQLITECPP_INTERNAL_SQLITE"] = False
        cmake.definitions["SQLITECPP_RUN_CPPLINT"] = self.options.lint
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        if "patches" in self.conan_data and self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)
        self._patch_clang()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "SQLiteCpp"
        self.cpp_info.names["cmake_find_package_multi"] = "SQLiteCpp"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
