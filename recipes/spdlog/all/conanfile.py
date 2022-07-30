from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.47.0"


class SpdlogConan(ConanFile):
    name = "spdlog"
    description = "Fast C++ logging library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gabime/spdlog"
    topics = ("logging", "log-filtering", "header-only")
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
        "wchar_support": [True, False],
        "wchar_filenames": [True, False],
        "no_exceptions": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
        "wchar_support": False,
        "wchar_filenames": False,
        "no_exceptions": False,
    }
    generators = "CMakeDeps"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.header_only:
            del self.options.shared
            del self.options.fPIC

    def requirements(self):
        if Version(self.version) >= "1.10.0":
            self.requires("fmt/8.1.1")
        elif Version(self.version) >= "1.9.0":
            self.requires("fmt/8.0.1")
        elif Version(self.version) >= "1.7.0":
            self.requires("fmt/7.1.3")
        elif Version(self.version) >= "1.5.0":
            self.requires("fmt/6.2.1")
        else:
            self.requires("fmt/6.0.0")

    def validate(self):
        if self.settings.os != "Windows" and (self.options.wchar_support or self.options.wchar_filenames):
            raise ConanInvalidConfiguration("wchar is only supported under windows")
        if self.options.get_safe("shared", False):
            if self.settings.os == "Windows" and Version(self.version) < "1.6.0":
                raise ConanInvalidConfiguration("spdlog shared lib is not yet supported under windows")
            if self.settings.compiler == "Visual Studio" and "MT" in self.settings.compiler.runtime:
                raise ConanInvalidConfiguration("Visual Studio build for shared library with MT runtime is not supported")
        if Version(self.version) < "1.7" and Version(self.deps_cpp_info["fmt"].version) >= "7":
            raise ConanInvalidConfiguration("The project {}/{} requires fmt < 7.x".format(self.name, self.version))

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not self.options.header_only:
            tc = CMakeToolchain(self)
            tc.variables["SPDLOG_BUILD_EXAMPLE"] = False
            tc.variables["SPDLOG_BUILD_EXAMPLE_HO"] = False
            tc.variables["SPDLOG_BUILD_TESTS"] = False
            tc.variables["SPDLOG_BUILD_TESTS_HO"] = False
            tc.variables["SPDLOG_BUILD_BENCH"] = False
            tc.variables["SPDLOG_FMT_EXTERNAL"] = True
            tc.variables["SPDLOG_FMT_EXTERNAL_HO"] = self.options["fmt"].header_only
            tc.variables["SPDLOG_BUILD_SHARED"] = not self.options.header_only and self.options.shared
            tc.variables["SPDLOG_WCHAR_SUPPORT"] = self.options.wchar_support
            tc.variables["SPDLOG_WCHAR_FILENAMES"] = self.options.wchar_filenames
            tc.variables["SPDLOG_INSTALL"] = True
            tc.variables["SPDLOG_NO_EXCEPTIONS"] = self.options.no_exceptions
            if self.settings.os in ("iOS", "tvOS", "watchOS"):
                self._cmake.definitions["SPDLOG_NO_TLS"] = True
            tc.generate()

    def layout(self):
        cmake_layout(self)

    def _disable_werror(self):
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "utils.cmake"), "/WX", "")

    def build(self):
        self._disable_werror()
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, "LICENSE", dst="licenses", src=self.source_folder)
        if self.options.header_only:
            copy(self, pattern="*.h", dst="include", src=os.path.join(self.source_folder, "include"))
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "lib", "spdlog", "cmake"))

    def package_info(self):
        target = "spdlog_header_only" if self.options.header_only else "spdlog"
        self.cpp_info.set_property("cmake_file_name", "spdlog")
        self.cpp_info.set_property("cmake_target_name", "spdlog::{}".format(target))
        self.cpp_info.set_property("pkg_config_name", "spdlog")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "spdlog"
        self.cpp_info.names["cmake_find_package_multi"] = "spdlog"
        self.cpp_info.components["libspdlog"].names["cmake_find_package"] = target
        self.cpp_info.components["libspdlog"].names["cmake_find_package_multi"] = target

        self.cpp_info.components["libspdlog"].defines.append("SPDLOG_FMT_EXTERNAL")
        self.cpp_info.components["libspdlog"].requires = ["fmt::fmt"]
        if not self.options.header_only:
            self.cpp_info.components["libspdlog"].libs = ["spdlog"]
            self.cpp_info.components["libspdlog"].defines.append("SPDLOG_COMPILED_LIB")
        if self.options.wchar_support:
            self.cpp_info.components["libspdlog"].defines.append("SPDLOG_WCHAR_TO_UTF8_SUPPORT")
        if self.options.wchar_filenames:
            self.cpp_info.components["libspdlog"].defines.append("SPDLOG_WCHAR_FILENAMES")
        if self.options.no_exceptions:
            self.cpp_info.components["libspdlog"].defines.append("SPDLOG_NO_EXCEPTIONS")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libspdlog"].system_libs = ["pthread"]
        if self.options.header_only and self.settings.os in ("iOS", "tvOS", "watchOS"):
            self.cpp_info.components["libspdlog"].defines.append("SPDLOG_NO_TLS")
