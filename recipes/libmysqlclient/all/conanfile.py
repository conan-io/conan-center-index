from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os
import glob


class LibMysqlClientCConan(ConanFile):
    name = "libmysqlclient"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A MySQL client library for C development."
    topics = ("conan", "mysql", "sql", "connector", "database")
    homepage = "https://dev.mysql.com/downloads/mysql/"
    license = "GPL-2.0"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "with_ssl": [True, False], "with_zlib": [True, False]}
    default_options = {"shared": False, "fPIC": True, "with_ssl": True, "with_zlib": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.with_ssl:
            self.requires("openssl/1.1.1g")

        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

    def source(self):
        archive_name = "mysql-" + self.version
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(archive_name, self._source_subfolder)
        for lib in ["icu", "libevent", "re2", "rapidjson", "lz4", "protobuf", "libedit"]:
            tools.rmdir(os.path.join(self._source_subfolder, "extra", lib))
        for folder in ['client', 'man', 'mysql-test']:
            tools.rmdir(os.path.join(self._source_subfolder, folder))
        tools.rmdir(os.path.join(self._source_subfolder, "storage", "ndb"))

    def _patch_files(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        sources_cmake = os.path.join(self._source_subfolder, "CMakeLists.txt")
        sources_cmake_orig = os.path.join(self._source_subfolder, "CMakeListsOriginal.txt")
        os.rename(sources_cmake, sources_cmake_orig)
        os.rename("CMakeLists.txt", sources_cmake)
        if self.settings.os == "Macos":
            tools.replace_in_file(os.path.join(self._source_subfolder, "libmysql", "CMakeLists.txt"), "COMMAND $<TARGET_FILE:libmysql_api_test>", "COMMAND DYLD_LIBRARY_PATH=%s $<TARGET_FILE:libmysql_api_test>" % os.path.join(self.build_folder, "library_output_directory"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.compiler == "Visual Studio":
            if Version(self.settings.compiler.version) < "15":
                raise ConanInvalidConfiguration("Visual Studio 15 2017 or newer is required")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version.value) < "5.3":
            raise ConanInvalidConfiguration("GCC 5.3 or newer is required")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DISABLE_SHARED"] = not self.options.shared
        self._cmake.definitions["STACK_DIRECTION"] = "-1"  # stack grows downwards, on very few platforms stack grows upwards
        self._cmake.definitions["WITHOUT_SERVER"] = True
        self._cmake.definitions["WITH_UNIT_TESTS"] = False
        self._cmake.definitions["ENABLED_PROFILING"] = False
        self._cmake.definitions["WIX_DIR"] = False

        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["WINDOWS_RUNTIME_MD"] = "MD" in str(self.settings.compiler.runtime)

        if self.options.with_ssl:
            self._cmake.definitions["WITH_SSL"] = self.deps_cpp_info["openssl"].rootpath

        if self.options.with_zlib:
            self._cmake.definitions["WITH_ZLIB"] = "system"

        self._cmake.configure(source_dir=self._source_subfolder)
        return self._cmake

    def build(self):
        self._patch_files()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        os.mkdir(os.path.join(self.package_folder, "licenses"))
        os.rename(os.path.join(self.package_folder, "LICENSE"), os.path.join(self.package_folder, "licenses", "LICENSE"))
        os.remove(os.path.join(self.package_folder, "README"))
        for f in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
            os.remove(f)
        for f in glob.glob(os.path.join(self.package_folder, "lib", "*.pdb")):
            os.remove(f)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "docs"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["libmysql" if self.settings.os == "Windows" and self.options.shared else "mysqlclient"]
