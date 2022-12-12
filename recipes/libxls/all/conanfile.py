from audioop import cross
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.files import export_conandata_patches, apply_conandata_patches, rmdir, copy, save, replace_in_file, get, rm
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.scm import Version

import os

required_conan_version = ">=1.53.0"

class LibxlsConan(ConanFile):
    name = "libxls"
    description = "a C library which can read Excel (xls) files."
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libxls/libxls/"
    topics = ("excel", "xls")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cli": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_cli": False,
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
        basic_layout(self, src_folder='src')

    def requirements(self):
        if not is_apple_os(self):
            self.requires("libiconv/1.17")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support Windows(yet).")

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.tool_requires("msys2/cci.latest")
            self.win_bash = True

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        toolchain = AutotoolsToolchain(self)
        if cross_building(self):
            toolchain.configure_args.append("ac_cv_func_malloc_0_nonnull=yes")
            toolchain.configure_args.append("ac_cv_func_realloc_0_nonnull=yes")
        toolchain.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def _patch_sources(self):
        config_h_content = """
#define HAVE_ICONV 1
#define ICONV_CONST
#define PACKAGE_VERSION "{}"
""".format(self.version)
        if self.settings.os == "Macos":
            config_h_content += "#define HAVE_XLOCALE_H 1\n"
        save(self, os.path.join(self.source_folder, "include", "config.h"), config_h_content)
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["xlsreader"]

        if is_apple_os(self):
            self.cpp_info.system_libs.append("iconv")

        self.cpp_info.set_property("cmake_file_name", "libxls")
        self.cpp_info.set_property("cmake_target_name", "libxls::libxls")
        self.cpp_info.set_property("pkg_config_name", "libxls")

        if not is_apple_os(self):
            self.cpp_info.requires.append("libiconv::libiconv")

        # TODO: Remove in Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "libxls"
        self.cpp_info.names["cmake_find_package_multi"] = "libxls"
