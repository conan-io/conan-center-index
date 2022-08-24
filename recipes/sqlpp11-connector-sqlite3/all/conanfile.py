from conan import ConanFile, tools
from conans import CMake
import os


class sqlpp11Conan(ConanFile):
    name = "sqlpp11-connector-sqlite3"
    description = "A C++ wrapper for sqlite3 meant to be used in combination with sqlpp11."
    topics = ("conan", "sqlpp11-connector-sqlite3", "sqlite3", "sqlpp11", "sql", "database")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rbock/sqlpp11-connector-sqlite3"
    license = "BSD-2-Clause"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    options = {"shared": [True, False], "fPIC": [True, False], "with_sqlcipher": [True, False]}
    default_options = {"shared": False, "fPIC": True, "with_sqlcipher": False}
    short_paths = True

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
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def requirements(self):
        self.requires("sqlpp11/0.59")
        if self.options.with_sqlcipher:
            self.requires("sqlcipher/4.4.0")
        else:
            self.requires("sqlite3/3.32.3")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_TESTS"] = False
        self._cmake.definitions["SQLCIPHER"] = self.options.with_sqlcipher
        self._cmake.definitions["SQLPP11_INCLUDE_DIR"] = self.deps_cpp_info["sqlpp11"].include_paths[0]
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["sqlpp11-connector-sqlite3"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
        if self.options.with_sqlcipher:
            self.cpp_info.defines = ["SQLPP_USE_SQLCIPHER"]
