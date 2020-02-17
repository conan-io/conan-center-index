from conans import ConanFile, tools, AutoToolsBuildEnvironment, CMake
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os


class LibpqxxRecipe(ConanFile):
    name = "libpqxx"
    settings = "os", "compiler", "build_type", "arch"
    description = "The official C++ client API for PostgreSQL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jtv/libpqxx"
    license = "BSD-3-Clause"
    topics = ("conan", "libpqxx", "postgres", "postgresql", "database", "db")
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = "libpq/11.5"
    _autotools = None
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _using_cmake(self):
        return self.settings.os == "Windows"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version.value)

        minimal_version = {
            "Visual Studio": "15",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10"
        }

        if compiler in minimal_version and \
           compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports"
                                            " at least C++17. %s %s is not"
                                            " supported." % (self.name, compiler, compiler_version))
        minimal_cpp_standard = "17"
        supported_cppstd = ["17", "20"]

        if not self.settings.compiler.cppstd:
            self.output.info("Settings c++ standard to {}".format(minimal_cpp_standard))
            self.settings.compiler.cppstd = minimal_cpp_standard

        if not self.settings.compiler.cppstd in supported_cppstd:
            raise ConanInvalidConfiguration(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

        if self.options.shared and \
           self.settings.os == "Windows" and \
           compiler == "Visual Studio":
            self.output.info("Override libpq:shared to True.")
            self.options["libpq"].shared = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            args = [
                "--disable-documentation",
                "--with-postgres-include={}".format(os.path.join(self.deps_cpp_info["libpq"].rootpath, "include")),
                "--with-postgres-lib={}".format(os.path.join(self.deps_cpp_info["libpq"].rootpath, "lib")),
                "--enable-static={}".format("no" if self.options.shared else "yes"),
                "--enable-shared={}".format("yes" if self.options.shared else "no")
            ]
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            env_vars = self._autotools.vars
            env_vars["PG_CONFIG"] = os.path.join(self.deps_cpp_info["libpq"].rootpath, "bin", "pg_config")
            self._autotools.configure(args=args, vars=env_vars)
        return self._autotools

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_DOC"] = False
            self._cmake.definitions["BUILD_TEST"] = False
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_files(self):
        if self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

    def build(self):
        self._patch_files()

        if self._using_cmake:
            cmake = self._configure_cmake()
            cmake.build()
        else:
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        if self._using_cmake:
            cmake = self._configure_cmake()
            cmake.install()

        else:
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.install()

    def package_info(self):
        pqxx_with_suffix = "pqxx-%s.%s" % tuple(self.version.split(".")[0:2])
        is_package_with_suffix = not (self._using_cmake and self.settings.os == "Windows") and \
                                 self.options.shared
        self.cpp_info.libs.append(pqxx_with_suffix if is_package_with_suffix else "pqxx")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["wsock32 ", "ws2_32"])
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
