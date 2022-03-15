import os
import shutil

from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, apply_conandata_patches
from conan.tools.microsoft.visual import is_msvc, msvc_runtime_flag
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class FmtConan(ConanFile):
    name = "fmt"
    homepage = "https://github.com/fmtlib/fmt"
    description = "A safe and fast alternative to printf and IOStreams."
    topics = ("fmt", "format", "iostream", "printf")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    exports_sources = "patches/*"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "header_only": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],
        "with_fmt_alias": [True, False],
        "with_os_api": [True, False],
    }
    default_options = {
        "header_only": False,
        "shared": False,
        "fPIC": True,
        "with_fmt_alias": False,
        "with_os_api": True,
    }

    @property
    def _has_with_os_api_option(self):
        return Version(str(self.version)) >= "7.0.0"

    def generate(self):
        if not self.options.header_only:
            tc = CMakeToolchain(self)
            tc.variables["FMT_DOC"] = False
            tc.variables["FMT_TEST"] = False
            tc.variables["FMT_INSTALL"] = True
            tc.variables["FMT_LIB_DIR"] = "lib"
            if self._has_with_os_api_option:
                tc.variables["FMT_OS"] = self.options.with_os_api
            tc.generate()  

    def layout(self):
        cmake_layout(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_with_os_api_option:
            del self.options.with_os_api
        elif str(self.settings.os) == "baremetal":
            self.options.with_os_api = False

    def configure(self):
        try:
            if self.options.header_only:
                del self.options.fPIC
                del self.options.shared
                del self.options.with_os_api
            elif self.options.shared:
                del self.options.fPIC
        except Exception:
            pass

    def validate(self):
        if self.options.get_safe("shared") and is_msvc(self) and "MT" in msvc_runtime_flag(self):
            raise ConanInvalidConfiguration(
                "Visual Studio build for shared library with MT runtime is not supported"
            )

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()
        else:
            del self.info.options.with_fmt_alias

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], destination=self.source_folder, strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    @staticmethod
    def _rm_folder(folder):
        try:
            shutil.rmtree(folder)
        except Exception:
            pass

    def package(self):
        copy(self, "LICENSE.rst", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if self.options.header_only:
            copy(self, "*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        else:
            cmake = CMake(self)
            cmake.install()
            self._rm_folder(os.path.join(self.package_folder, "lib", "cmake"))
            self._rm_folder(os.path.join(self.package_folder, "lib", "pkgconfig"))
            self._rm_folder(os.path.join(self.package_folder, "res"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "fmt"
        self.cpp_info.names["cmake_find_package_multi"] = "fmt"
        self.cpp_info.names["pkg_config"] = "fmt"
        if self.options.header_only:
            self.cpp_info.components["fmt-header-only"].defines.append("FMT_HEADER_ONLY=1")
            if self.options.with_fmt_alias:
                self.cpp_info.components["fmt-header-only"].defines.append("FMT_STRING_ALIAS=1")
        else:
            postfix = "d" if self.settings.build_type == "Debug" else ""
            self.cpp_info.libs = ["fmt" + postfix]
            if self.options.with_fmt_alias:
                self.cpp_info.defines.append("FMT_STRING_ALIAS=1")
            if self.options.shared:
                self.cpp_info.defines.append("FMT_SHARED")
