from conans import ConanFile, CMake, tools
import os
import shutil

required_conan_version = ">=1.33.0"

class DuckdbConan(ConanFile):
    name = "duckdb"
    license = "MIT"
    homepage = "https://github.com/cwida/duckdb"
    url = "https://github.com/conan-io/conan-center-index/"
    description = "DuckDB is an embeddable SQL OLAP Database Management System"
    topics = ("sql", "database", "olap", "embedded-database")
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_icu": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_icu": False,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def source(self):
        tools.get(**(self.conan_data["sources"][self.version][0]),
                  destination=self._source_subfolder, strip_root=True)
        tools.get(**(self.conan_data["sources"][self.version][1]),
                  destination=os.path.join(self._source_subfolder, "src", "amalgamation"))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["AMALGAMATION_BUILD"] = True
        self._cmake.definitions["BUILD_UNITTESTS"] = False
        self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        self._cmake.definitions["BUILD_ICU_EXTENSION"] = self.options.with_icu
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["duckdb"]  
        else:
            self.cpp_info.libs = ["duckdb_static"]
            if self.options.with_icu:
                self.cpp_info.libs.append("icu_extension")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl"]
