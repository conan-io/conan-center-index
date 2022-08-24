from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os


class MysqlConnectorCConan(ConanFile):
    name = "mysql-connector-c"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A MySQL client library for C development."
    topics = ("mysql", "sql", "connector", "database")
    homepage = "https://dev.mysql.com/downloads/connector/c/"
    license = "GPL-2.0"
    exports_sources = ["CMakeLists.txt", "patches/*.patch"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "with_ssl": [True, False], "with_zlib": [True, False]}
    default_options = {'shared': False, 'with_ssl': True, 'with_zlib': True}
    
    deprecated = "libmysqlclient"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.with_ssl:
            self.requires("openssl/1.0.2u")

        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

    def validate(self):
        if hasattr(self, "settings_build") and tools.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross compilation not yet supported by the recipe. contributions are welcome.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["DISABLE_SHARED"] = not self.options.shared
        self._cmake.definitions["DISABLE_STATIC"] = self.options.shared
        self._cmake.definitions["STACK_DIRECTION"] = "-1"  # stack grows downwards, on very few platforms stack grows upwards
        self._cmake.definitions["REQUIRE_STDCPP"] = tools.stdcpp_library(self)

        if self.settings.compiler == "Visual Studio":
            if self.settings.compiler.runtime == "MD" or self.settings.compiler.runtime == "MDd":
                self._cmake.definitions["WINDOWS_RUNTIME_MD"] = True

        if self.options.with_ssl:
            self._cmake.definitions["WITH_SSL"] = "system"

        if self.options.with_zlib:
            self._cmake.definitions["WITH_ZLIB"] = "system"

        self._cmake.configure(source_dir=self._source_subfolder)
        return self._cmake

    def _patch_sources(self):
        sources_cmake = os.path.join(self._source_subfolder, "CMakeLists.txt")
        sources_cmake_orig = os.path.join(self._source_subfolder, "CMakeListsOriginal.txt")

        tools.files.rename(self, sources_cmake, sources_cmake_orig)
        tools.files.rename(self, "CMakeLists.txt", sources_cmake)

        for patch in self.conan_data["patches"][self.version]:
            tools.files.patch(self, **patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.mkdir(os.path.join(self.package_folder, "licenses"))
        tools.files.rename(self, os.path.join(self.package_folder, "COPYING"), os.path.join(self.package_folder, "licenses", "COPYING"))
        tools.files.rename(self, os.path.join(self.package_folder, "COPYING-debug"), os.path.join(self.package_folder, "licenses", "COPYING-debug"))
        tools.files.rm(self, self.package_folder, "README*")
        tools.files.rm(self, self.package_folder, "*.pdb")
        tools.files.rmdir(self, os.path.join(self.package_folder, "docs"))

    def package_info(self):
        self.cpp_info.libs = ["libmysql" if self.options.shared and self.settings.os == "Windows" else "mysqlclient"]
        if not self.options.shared:
            stdcpp_library = tools.stdcpp_library(self)
            if stdcpp_library:
                self.cpp_info.system_libs.append(stdcpp_library)
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append('m')
