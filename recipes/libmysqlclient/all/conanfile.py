from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os
import glob


class libMysqlClientCConan(ConanFile):
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
    default_options = {"shared": True, "fPIC": True, "with_ssl": True, "with_zlib": True}
    _source_subfolder = "source_subfolder"

    def requirements(self):
        if self.options.with_ssl:
            self.requires("openssl/1.1.1f")

        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        archive_name = "mysql-" + self.version
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(archive_name, self._source_subfolder)
        for lib in ["icu", "libevent", "re2", "rapidjson", "lz4", "protobuf", "libedit"]:
            tools.rmdir(os.path.join(self._source_subfolder, "extra", lib))
        for folder in ['client', 'man', 'mysql-test']:
            tools.rmdir(os.path.join(self._source_subfolder, folder))
        tools.rmdir(os.path.join(self._source_subfolder, "storage", "ndb"))

    def _patch(self):
        tools.patch(**self.conan_data["patches"][self.version])
        sources_cmake = os.path.join(self._source_subfolder, "CMakeLists.txt")
        sources_cmake_orig = os.path.join(self._source_subfolder, "CMakeListsOriginal.txt")
        os.rename(sources_cmake, sources_cmake_orig)
        os.rename("CMakeLists.txt", sources_cmake)
        if self.settings.os == "Macos":
            tools.replace_in_file(os.path.join(self._source_subfolder, "libmysql", "CMakeLists.txt"), "COMMAND $<TARGET_FILE:libmysql_api_test>", "COMMAND DYLD_LIBRARY_PATH=%s $<TARGET_FILE:libmysql_api_test>" % os.path.join(self.build_folder, "library_output_directory"))

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if not self.options.shared:
            raise ConanInvalidConfiguration("libmysqlclient cannot be built as static library")
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio is not supported yet")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version.value) < "5.3":
            raise ConanInvalidConfiguration("GCC 5.3 or newer is required")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["DISABLE_SHARED"] = not self.options.shared
        cmake.definitions["STACK_DIRECTION"] = "-1"  # stack grows downwards, on very few platforms stack grows upwards
        cmake.definitions["WITHOUT_SERVER"] = True
        cmake.definitions["WITH_UNIT_TESTS"] = False
        cmake.definitions["ENABLED_PROFILING"] = False
        cmake.definitions["WIX_DIR"] = False

        if self.settings.compiler == "Visual Studio":
            if self.settings.compiler.runtime == "MD" or self.settings.compiler.runtime == "MDd":
                cmake.definitions["WINDOWS_RUNTIME_MD"] = True

        if self.options.with_ssl:
            cmake.definitions["WITH_SSL"] = self.deps_cpp_info["openssl"].rootpath

        if self.options.with_zlib:
            cmake.definitions["WITH_ZLIB"] = "system"

        cmake.configure(source_dir=self._source_subfolder)
        return cmake

    def build(self):
        self._patch()
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
        self.cpp_info.libs = tools.collect_libs(self)
