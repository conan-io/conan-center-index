from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class SQLiteCppConan(ConanFile):
    name = "sqlitecpp"
    description = "SQLiteCpp is a smart and easy to use C++ sqlite3 wrapper"
    topics = ("conan", "sqlitecpp", "sqlite3")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/SRombauts/SQLiteCpp"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "lint": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "lint": False,
    }

    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    _cmake = None

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
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("sqlite3/3.36.0")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("SQLiteCpp can not be built as shared lib on Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.compiler == "clang" and \
           tools.Version(self.settings.compiler.version) < "6.0" and \
           self.settings.compiler.libcxx == "libc++" and \
           tools.Version(self.version) < "3":
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "include", "SQLiteCpp", "Utils.h"),
                "const nullptr_t nullptr = {};",
                "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SQLITECPP_INTERNAL_SQLITE"] = False
        self._cmake.definitions["SQLITECPP_RUN_CPPLINT"] = self.options.lint
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
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
