from conan.tools.microsoft import msvc_runtime_flag
from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.43.0"


class LibpqxxConan(ConanFile):
    name = "libpqxx"
    description = "The official C++ client API for PostgreSQL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jtv/libpqxx"
    license = "BSD-3-Clause"
    topics = ("libpqxx", "postgres", "postgresql", "database", "db")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _mac_os_minimum_required_version(self):
        return "10.15"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libpq/14.2")

    def validate(self):
        if self.options.shared and msvc_runtime_flag(self) == "MTd":
            raise ConanInvalidConfiguration(
                "{} recipes does not support build shared library with MTd runtime."
                .format(self.name,))

        compiler = str(self.settings.compiler)
        compiler_version = tools.Version(self.settings.compiler.version)

        lib_version = tools.Version(self.version)
        lib_version_7_6_0_or_later = lib_version >= "7.6.0"
        minimum_compiler_version = {
            "Visual Studio": "16" if lib_version_7_6_0_or_later else "15",
            "msvc": "192" if lib_version_7_6_0_or_later else "191",
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
            if os_version and tools.Version(os_version) < self._mac_os_minimum_required_version:
                raise ConanInvalidConfiguration(
                    "Macos Mojave (10.14) and earlier cannot to be built because C++ standard library too old.")

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, minimum_cpp_standard)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_DOC"] = False
        cmake.definitions["BUILD_TEST"] = False
        # Set `-mmacosx-version-min` to enable C++17 standard library support.
        cmake.definitions["CMAKE_OSX_DEPLOYMENT_TARGET"] = self._mac_os_minimum_required_version
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
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
        self.cpp_info.set_property("cmake_file_name", "libpqxx")
        self.cpp_info.set_property("cmake_target_name", "libpqxx::pqxx")
        self.cpp_info.set_property("pkg_config_name", "libpqxx")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["pqxx"].libs = ["pqxx"]
        if self.settings.os == "Windows":
            self.cpp_info.components["pqxx"].system_libs = ["wsock32", "ws2_32"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["pqxx"].set_property("cmake_target_name", "libpqxx::pqxx")
        self.cpp_info.components["pqxx"].set_property("pkg_config_name", "libpqxx")
        self.cpp_info.components["pqxx"].requires = ["libpq::libpq"]
