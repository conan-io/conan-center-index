from conans import ConanFile, CMake, tools
import os


class sqlpp11Conan(ConanFile):
    name = "sqlpp11-connector-sqlite3"
    description = "A C++ wrapper for sqlite3 meant to be used in combination with sqlpp11."
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rbock/sqlpp11-connector-sqlite3"
    license = "BSD-2-Clause"
    exports_sources = ["CMakeLists.txt"]
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

    def requirements(self):
        self.requires("sqlpp11/0.58")
        if self.options.with_sqlcipher:
            self.requires("sqlcipher/4.3.0")
        else:
            self.requires("sqlite3/3.30.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
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
