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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version.value)

        lib_version_7_5_0_or_above = Version(self.version) >= "7.5.0"
        gcc_minimal_version = "8" if lib_version_7_5_0_or_above else "7"
        visual_studio_minimal_version = "16" if lib_version_7_5_0_or_above else "15"
        minimum_compiler_version = {
            "Visual Studio": visual_studio_minimal_version,
            "gcc": gcc_minimal_version,
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

        if self.settings.os == "Macos" and Version(self.settings.os.version) < "10.15":
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
