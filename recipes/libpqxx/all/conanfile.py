from conans import ConanFile, tools, CMake
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
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _mac_os_minimum_required_version(self):
        return "10.15"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version.value)

        lib_version = Version(self.version)
        minimum_compiler_version = {
            "Visual Studio": "16" if lib_version >= "7.6.0" else "15",
            "gcc": "8" if lib_version >= "7.5.0" else "7",
            "clang": "6",
            "apple-clang": "10"
        }

        minimum_cpp_standard = 17

        if compiler in minimum_compiler_version and \
           compiler_version < minimum_compiler_version[compiler]:
            raise ConanInvalidConfiguration("{} requires a compiler that supports"
                                            " at least C++{}. {} {} is not"
                                            " supported."
                                            .format(self.name, minimum_cpp_standard, compiler, compiler_version))

        if self.settings.os == "Macos":
            os_version = self.settings.get_safe("os.version")
            if os_version and Version(os_version) < self._mac_os_minimum_required_version:
                raise ConanInvalidConfiguration(
                    "Macos Mojave (10.14) and earlier cannot to be built because C++ standard library too old.")

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, minimum_cpp_standard)

    def requirements(self):
        self.requires("libpq/12.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_DOC"] = False
            self._cmake.definitions["BUILD_TEST"] = False
            # Set `-mmacosx-version-min` to enable C++17 standard library support.
            self._cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = self._mac_os_minimum_required_version
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_files(self):
        if self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

    def build(self):
        self._patch_files()

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.components["pqxx"].libs = ["pqxx"]
        self.cpp_info.components["pqxx"].requires = ["libpq::libpq"]
        if self.settings.os == "Windows":
            self.cpp_info.components["pqxx"].system_libs = ["wsock32", "ws2_32"]
