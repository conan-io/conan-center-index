from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.54.0"


class Log4cxx(ConanFile):
    name = "log4cxx"
    description = "Logging framework for C++ patterned after Apache log4j"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    homepage = "https://logging.apache.org/log4cxx"
    topics = ("logging")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_networking": [True, False],
        "with_wchar_t": [True, False],
        "with_odbc": [True, False],
        "with_multiprocess_rolling_file_appender": [True, False],
        "with_qt": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_networking": True,
        "with_wchar_t": False,
        "with_odbc": False,
        "with_multiprocess_rolling_file_appender": False,
        "with_qt": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        if Version(self.version) < "1.0.0":
            self.options.rm_safe("with_multiprocess_rolling_file_appender")
            self.options.rm_safe("with_networking")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("apr/[>=1.6]")
        self.requires("apr-util/[>=1.6]")
        self.requires("expat/[>=2.4]")
        if self.options.get_safe("with_odbc") and self.settings.os != "Windows":
            self.requires("odbc/[>=2.3]")
        if self.options.get_safe("with_qt"):
            self.requires("qt/[>=5.15 <6]")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15",
            "msvc": "191",
            "clang": "5",
            "apple-clang": "10",
        }

    def validate(self):
        if self.options.get_safe("with_multiprocess_rolling_file_appender"):
            # TODO: if compiler doesn't support C++17, boost can be used instead
            self.output.warning("multiprocess rolling file appender requires C++17.")
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            compiler_version = Version(self.settings.compiler.version)
            if not minimum_version:
                self.output.warning("Your compiler is unknown. Assuming it supports C++17.")
            elif compiler_version < minimum_version:
                raise ConanInvalidConfiguration(f"{self.settings.compiler} {compiler_version} does not support C++17: {minimum_version} required.")
            if self.settings.compiler.get_safe("cppstd"):
                check_min_cppstd(self, "17")

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.tool_requires("pkgconf/1.7.4")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        if Version(self.version) >= "1.0.0":
            tc.variables["LOG4CXX_NETWORKING_SUPPORT"] = self.options.with_networking
            tc.variables["LOG4CXX_MULTIPROCESS_ROLLING_FILE_APPENDER"] = self.options.with_multiprocess_rolling_file_appender
        tc.variables["LOG4CXX_ENABLE_ODBC"] = self.options.with_odbc
        tc.variables["LOG4CXX_WCHAR_T"] = self.options.with_wchar_t
        tc.variables["LOG4CXX_QT_SUPPORT"] = self.options.with_qt
        if self.settings.os == "Windows":
            tc.variables["LOG4CXX_INSTALL_PDB"] = False
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst="licenses")
        copy(self, "NOTICE", src=self.source_folder, dst="licenses")
        cmake = CMake(self)
        cmake.install()
        if self.settings.os != "Windows":
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "log4cxx")
        self.cpp_info.set_property("cmake_target_name", "log4cxx")
        self.cpp_info.set_property("pkg_config_name", "liblog4cxx")
        self.cpp_info.libs = ["log4cxx"]
        if not self.options.shared:
            self.cpp_info.defines = ["LOG4CXX_STATIC"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["odbc32"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
