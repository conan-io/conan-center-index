from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import cross_building, stdcpp_library
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir, save, rename, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path, check_min_vs
import os

required_conan_version = ">=1.54.0"


class DjVuLibreConan(ConanFile):
    name = "djvulibre"
    description = "Library and utilities to create, manipulate and view DjVu documents"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://djvu.sourceforge.net/"
    topics = ("djvu", "file-format", "document-format")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": False,
        "with_libjpeg": "libjpeg",
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")
        if self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.2")
        elif self.options.with_libjpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")
        self.requires("libtiff/4.6.0")

    def validate(self):
        if self.settings.os == "Windows" and not self.options.shared:
            # __declspec(dllimport) or __declspec(dllexport) is always set for symbols
            raise ConanInvalidConfiguration("Static linking is not supported on Windows")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()
        if not cross_building(self):
            VirtualRunEnv(self).generate(scope="build")

        tc = AutotoolsToolchain(self)
        jpeg = self.dependencies[self.options.with_libjpeg.value].cpp_info.aggregated_components()
        tiff = self.dependencies["libtiff"].cpp_info.aggregated_components()
        tc.configure_args.extend([
            f"JPEG_LIBS={' '.join(f'-l{l}' for l in jpeg.libs)}",
            f"TIFF_LIBS={' '.join(f'-l{l}' for l in tiff.libs)}",
        ])
        if is_msvc(self):
            tc.extra_cxxflags.append("-EHsc")
            if check_min_vs(self, "180", raise_invalid=False):
                tc.extra_cflags.append("-FS")
                tc.extra_cxxflags.append("-FS")
            tc.extra_ldflags.append("-ladvapi32")
        tc.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} lib")
            env.define("NM", "dumpbin -symbols")
            env.vars(self).save_script("conanbuild_msvc")

        if is_msvc(self):
            # Custom AutotoolsDeps for cl-like compilers
            # workaround for https://github.com/conan-io/conan/issues/12784
            includedirs = []
            defines = []
            libs = []
            libdirs = []
            linkflags = []
            cxxflags = []
            cflags = []
            for dependency in self.dependencies.values():
                deps_cpp_info = dependency.cpp_info.aggregated_components()
                includedirs.extend(deps_cpp_info.includedirs)
                defines.extend(deps_cpp_info.defines)
                libs.extend(deps_cpp_info.libs + deps_cpp_info.system_libs)
                libdirs.extend(deps_cpp_info.libdirs)
                linkflags.extend(deps_cpp_info.sharedlinkflags + deps_cpp_info.exelinkflags)
                cxxflags.extend(deps_cpp_info.cxxflags)
                cflags.extend(deps_cpp_info.cflags)

            env = Environment()
            env.append("CPPFLAGS", [f"-I{unix_path(self, p)}" for p in includedirs] + [f"-D{d}" for d in defines])
            env.append("_LINK_", [lib if lib.endswith(".lib") else f"{lib}.lib" for lib in libs])
            env.append("LDFLAGS", [f"-L{unix_path(self, p)}" for p in libdirs] + linkflags)
            env.append("CXXFLAGS", cxxflags)
            env.append("CFLAGS", cflags)
            env.vars(self).save_script("conanautotoolsdeps_cl_workaround")
        else:
            deps = AutotoolsDeps(self)
            deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if not self.options.tools:
            save(self, os.path.join(self.source_folder, "tools", "Makefile.am"), "")
            save(self, os.path.join(self.source_folder, "xmltools", "Makefile.am"), "")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share", "man"))
        rmdir(self, os.path.join(self.package_folder, "share", "icons"))
        rename(self, os.path.join(self.package_folder, "share"), os.path.join(self.package_folder, "res"))
        fix_apple_shared_install_name(self)
        if is_msvc(self) and self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "djvulibre.dll.lib"),
                         os.path.join(self.package_folder, "lib", "djvulibre.lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "ddjvuapi")
        self.cpp_info.libs = ["djvulibre"]
        self.cpp_info.resdirs = ["res"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        elif is_apple_os(self):
            self.cpp_info.frameworks.extend(["CoreFoundation"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("advapi32")

        # Implemented in C++ but exports a pure C API
        if stdcpp_library(self):
            self.cpp_info.system_libs.append(stdcpp_library(self))
