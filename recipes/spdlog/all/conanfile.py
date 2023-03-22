from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class SpdlogConan(ConanFile):
    name = "spdlog"
    package_type = "library"
    description = "Fast C++ logging library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gabime/spdlog"
    topics = ("logger", "logging", "log-filtering", "file sink", "header-only")
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.get_safe("shared") or self.options.header_only:
            self.options.rm_safe("fPIC")
        if self.options.header_only:
            self.options.rm_safe("shared")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self_version = Version(self.version)
        fmt_version = "7.1.3"

        if self_version >= "1.11.0":
            fmt_version = "9.1.0"
        elif self_version >= "1.10.0":
            fmt_version = "8.1.1"
        elif self_version >= "1.9.0":
            fmt_version = "8.0.1"
        elif self_version >= "1.7.0":
            fmt_version = "7.1.3"

        self.requires(f"fmt/{fmt_version}", transitive_headers=True, transitive_libs=True)

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 11)
        if self.settings.os != "Windows" and (self.options.wchar_support or self.options.wchar_filenames):
            raise ConanInvalidConfiguration("wchar is only supported under windows")
        if self.options.get_safe("shared") and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio build for shared library with MT runtime is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not self.options.header_only:
            fmt = self.dependencies["fmt"]
            tc = CMakeToolchain(self)
            tc.variables["SPDLOG_BUILD_EXAMPLE"] = False
            tc.variables["SPDLOG_BUILD_EXAMPLE_HO"] = False
            tc.variables["SPDLOG_BUILD_TESTS"] = False
            tc.variables["SPDLOG_BUILD_TESTS_HO"] = False
            tc.variables["SPDLOG_BUILD_BENCH"] = False
            tc.variables["SPDLOG_FMT_EXTERNAL"] = not fmt.options.header_only
            tc.variables["SPDLOG_FMT_EXTERNAL_HO"] = fmt.options.header_only
            tc.variables["SPDLOG_BUILD_SHARED"] = not self.options.header_only and self.options.shared
            tc.variables["SPDLOG_WCHAR_SUPPORT"] = self.options.wchar_support
            tc.variables["SPDLOG_WCHAR_FILENAMES"] = self.options.wchar_filenames
            tc.variables["SPDLOG_INSTALL"] = True
            tc.variables["SPDLOG_NO_EXCEPTIONS"] = self.options.no_exceptions
            if self.settings.os in ("iOS", "tvOS", "watchOS"):
                tc.variables["SPDLOG_NO_TLS"] = True
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0091"] = "NEW"
            tc.generate()
        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()

    def _disable_werror(self):
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "utils.cmake"), "/WX", "")

    def build(self):
        self._disable_werror()
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.options.header_only:
            copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "lib", "spdlog", "cmake"))

    def package_info(self):
        target = "spdlog_header_only" if self.options.header_only else "spdlog"
        self.cpp_info.set_property("cmake_file_name", "spdlog")
        self.cpp_info.set_property("cmake_target_name", f"spdlog::{target}")
        self.cpp_info.set_property("pkg_config_name", "spdlog")

        # TODO: back to global scope in conan v2 once legacy generators removed
        self.cpp_info.components["libspdlog"].set_property("cmake_target_name", f"spdlog::{target}")
        self.cpp_info.components["libspdlog"].defines.append("SPDLOG_FMT_EXTERNAL")
        self.cpp_info.components["libspdlog"].requires = ["fmt::fmt"]

        if not self.options.header_only:
            suffix = "d" if self.settings.build_type == "Debug" else ""
            self.cpp_info.components["libspdlog"].libs = [f"spdlog{suffix}"]
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

        self.cpp_info.names["cmake_find_package"] = "spdlog"
        self.cpp_info.names["cmake_find_package_multi"] = "spdlog"
        self.cpp_info.components["libspdlog"].names["cmake_find_package"] = target
        self.cpp_info.components["libspdlog"].names["cmake_find_package_multi"] = target
