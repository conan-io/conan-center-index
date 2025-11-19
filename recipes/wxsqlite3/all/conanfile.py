import os

from conan import ConanFile
from conan.tools.files import copy, get, rmdir, rm, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import cross_building
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.1"

class WxSqLite3Conan(ConanFile):
    name = "wxsqlite3"
    description = "wxSQLite3 is a C++ wrapper around the SQLite database designed for use in wxWidgets applications."
    license = "LGPL-3.0+ WITH WxWindows-exception-3.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://utelle.github.io/wxsqlite3/docs/html/index.html"
    topics = ("wxwidgets", "sqlite", "sqlite3", "sql", "database")
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = { "shared": [True, False] }
    options = { "shared": [True, False], "fPIC": [True, False] }
    default_options = { "shared": False, "fPIC": True }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def requirements(self):
        # https://github.com/utelle/wxsqlite3/blob/v4.10.8/premake/wxwidgets.lua#L146
        self.requires("wxwidgets/[>=3.2.5 <3.3]", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.tool_requires("libtool/2.4.7")

    def generate(self):
        if self.settings.os == "Windows":
            deps = CMakeDeps(self)
            deps.generate()
            tc = CMakeToolchain(self)
            tc.cache_variables["WXSQLITE3_BUILD_SHARED"] = self.options.shared
            tc.cache_variables["STATIC_RUNTIME"] = is_msvc_static_runtime(self)
            tc.cache_variables["PEDANTIC_COMPILER_FLAGS"] = False
            tc.generate()
        else:
            wxwidgets_root = self.dependencies["wxwidgets"].package_folder
            wx_config = os.path.join(wxwidgets_root, "bin", "wx-config")
            tc = AutotoolsToolchain(self)
            tc.configure_args.append(f"--with-wx-config={wx_config}")
            tc.configure_args.append(f"--with-wx-prefix={wxwidgets_root}")
            tc.generate()
            deps = AutotoolsDeps(self)
            deps.generate()

    def validate(self):
        if cross_building(self) and is_apple_os(self):
            # FIXME: WxWidgets wx-config can not find the correct paths/libs when cross-building for Apple platforms
            raise ConanInvalidConfiguration("Cross-building wxsqlite3 for Apple platforms is not supported yet. Contributions are welcome!")

    def build(self):
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure(build_script_folder=os.path.join(self.source_folder, "build"))
            cmake.build(target="wxsqlite3")
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        if self.settings.os == "Windows":
            copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
            copy(self, "*.lib", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dll", self.build_folder, os.path.join(self.package_folder, "bin"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

        license_files = [
            "COPYING.txt",
            "GPL-3.0.txt",
            "LGPL-3.0.txt",
            "LICENSE.spdx",
            "LICENSE.txt",
            "WxWindows-exception-3.1.txt",
        ]

        for license_file in license_files:
            copy(self, license_file, dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["wxsqlite3"]
        elif self.settings.os == "Macos":
            self.cpp_info.libs = ["wxcode_osx_cocoau_wxsqlite3-3.2"]
        else:
            self.cpp_info.libs = ["wxcode_gtk2u_wxsqlite3-3.2"]
