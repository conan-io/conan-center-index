import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class TidyHtml5Conan(ConanFile):
    name = "tidy-html5"
    description = "The granddaddy of HTML tools, with support for modern standards"
    license = "HTMLTIDY"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.html-tidy.org"
    topics = ("html", "parser", "xml", "tools")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "support_localizations": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "support_localizations": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TAB2SPACE"] = False
        tc.variables["BUILD_SAMPLE_CODE"] = False
        tc.variables["TIDY_COMPAT_HEADERS"] = False
        tc.variables["SUPPORT_CONSOLE_APP"] = False
        tc.variables["SUPPORT_LOCALIZATIONS"] = self.options.support_localizations
        tc.variables["ENABLE_DEBUG_LOG"] = False
        tc.variables["ENABLE_ALLOC_DEBUG"] = False
        tc.variables["ENABLE_MEMORY_DEBUG"] = False
        tc.variables["BUILD_SHARED_LIB"] = self.options.shared
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "LICENSE.md",
             dst=os.path.join(self.package_folder, "licenses"),
             src=os.path.join(self.source_folder, "README"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"), recursive=True)
        if self.options.shared:
            to_remove = "*tidy_static*" if self.settings.os == "Windows" else "*.a"
            rm(self, to_remove, os.path.join(self.package_folder, "lib"), recursive=True)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "tidy")
        suffix = ""
        if self.settings.os == "Windows" and not self.options.shared:
            suffix = "_static"
        if is_msvc(self) and self.settings.build_type == "Debug":
            suffix += "d"
        self.cpp_info.libs = ["tidy" + suffix]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("TIDY_STATIC")
