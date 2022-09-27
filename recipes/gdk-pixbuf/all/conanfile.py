from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.gnu import PkgConfigDeps
from conan.tools.env import VirtualBuildEnv
from conan.tools.layout import basic_layout
from conan.tools import files, scm, microsoft
from conan.errors import ConanInvalidConfiguration, ConanException
from tempfile import TemporaryDirectory
import functools
import os

required_conan_version = ">=1.50.2"


class GdkPixbufConan(ConanFile):
    name = "gdk-pixbuf"
    description = "toolkit for image loading and pixel buffer manipulation"
    topics = ("gdk-pixbuf", "image")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.gnome.org/gdk-pixbuf/"
    license = "LGPL-2.1-or-later"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libpng": [True, False],
        "with_libtiff": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo", False],
        "with_introspection": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libpng": True,
        "with_libtiff": True,
        "with_libjpeg": "libjpeg",
        "with_introspection": False,
    }

    exports_sources = "patches/**"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            self.options["glib"].shared = True

    def layout(self):
        basic_layout(self, src_folder="source")

    @property
    def _requires_compiler_rt(self):
        return self.settings.compiler == "clang" and self.settings.build_type == "Debug"

    def _test_for_compiler_rt(self):
        cmake = CMake(self)
        with TemporaryDirectory() as tmp:
            def open_temp_file(file_name):
                return open(os.path.join(tmp, file_name), "w", encoding="utf-8")

            with open_temp_file("CMakeLists.txt") as cmake_file:
                cmake_file.write(r"""
                        cmake_minimum_required(VERSION 3.16)
                        project(compiler_rt_test)
                        try_compile(HAS_COMPILER_RT ${CMAKE_BINARY_DIR} ${CMAKE_SOURCE_DIR}/test.c OUTPUT_VARIABLE OUTPUT)
                        if(NOT HAS_COMPILER_RT)
                        message(FATAL_ERROR compiler-rt not present)
                        endif()""")
            with open_temp_file("test.c") as test_source:
                test_source.write(r"""
                        extern __int128_t __muloti4(__int128_t a, __int128_t b, int* overflow);
                        int main() {
                            __int128_t a;
                            __int128_t b;
                            int overflow;
                            __muloti4(a, b, &overflow);
                            return 0;
                        }""")
            cmake.definitions["CMAKE_EXE_LINKER_FLAGS"] = "-rtlib=compiler-rt"
            try:
                cmake.configure(build_script_folder=tmp)
            except ConanException as ex:
                raise ConanInvalidConfiguration("LLVM Compiler RT is required to link gdk-pixbuf in debug mode") from ex

    def generate(self):
        deps = PkgConfigDeps(self)
        deps.generate()

        tc = MesonToolchain(self)
        defs = {}
        if scm.Version(self.version) >= "2.42.0":
            defs["introspection"] = "false"
        else:
            defs["gir"] = "false"
        defs["docs"] = "false"
        defs["man"] = "false"
        defs["installed_tests"] = "false"
        if scm.Version(self.version) >= "2.42.8":
            defs["png"] = "enabled" if self.options.with_libpng else "disabled"
            defs["tiff"] = "enabled" if self.options.with_libtiff else "disabled"
            defs["jpeg"] = "enabled" if self.options.with_libjpeg else "disabled"
        else:
            defs["png"] = "true" if self.options.with_libpng else "false"
            defs["tiff"] = "true" if self.options.with_libtiff else "false"
            defs["jpeg"] = "true" if self.options.with_libjpeg else "false"

        defs["builtin_loaders"] = "all"
        defs["gio_sniffing"] = "false"
        defs["introspection"] = "enabled" if self.options.with_introspection else "disabled"
        tc.project_options.update(defs)

        # Workaround for https://bugs.llvm.org/show_bug.cgi?id=16404
        # Only really for the purposes of building on CCI - end users can
        # workaround this by appropriately setting global linker flags in their profile
        if self._requires_compiler_rt:
            self._test_for_compiler_rt()
            tc.c_link_args.append("-rtlib=compiler-rt")

        tc.generate()

        venv = VirtualBuildEnv(self)
        venv.generate()

    def requirements(self):
        self.requires("glib/2.74.0")
        if self.options.with_libpng:
            self.requires("libpng/1.6.38")
        if self.options.with_libtiff:
            self.requires("libtiff/4.4.0")
        if self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.4")
        elif self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")

    def validate(self):
        if self.options.shared and not self.options["glib"].shared:
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )
        if self.settings.os == "Macos":
            # when running gdk-pixbuf-query-loaders
            # dyld: malformed mach-o: load commands size (97560) > 32768
            raise ConanInvalidConfiguration("This package does not support Macos currently")

    def build_requirements(self):
        self.tool_requires("meson/0.63.2")
        self.tool_requires("pkgconf/1.9.3")
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/1.72.0")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        files.apply_conandata_patches(self)

        meson_build = os.path.join(self.source_folder, "meson.build")
        files.replace_in_file(self, meson_build, "subdir('tests')", "#subdir('tests')")
        files.replace_in_file(self, meson_build, "subdir('thumbnailer')", "#subdir('thumbnailer')")
        files.replace_in_file(self, meson_build,
                              "gmodule_dep.get_variable(pkgconfig: 'gmodule_supported')" if scm.Version(self.version) >= "2.42.6"
                              else "gmodule_dep.get_pkgconfig_variable('gmodule_supported')", "'true'")
        # workaround https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/issues/203
        if scm.Version(self.version) >= "2.42.6":
            files.replace_in_file(self, os.path.join(self.source_folder, "build-aux", "post-install.py"),
                                  "close_fds=True", "close_fds=(sys.platform != 'win32')")
        if scm.Version(self.version) >= "2.42.9":
            files.replace_in_file(self, meson_build, "is_msvc_like ? 'png' : 'libpng'", "'libpng'")
            files.replace_in_file(self, meson_build, "is_msvc_like ? 'jpeg' : 'libjpeg'", "'libjpeg'")
            files.replace_in_file(self, meson_build, "is_msvc_like ? 'tiff' : 'libtiff-4'", "'libtiff-4'")

    @functools.lru_cache(1)
    def _configure_meson(self):
        meson = Meson(self)
        meson.configure()
        return meson

    def build(self):
        self._patch_sources()
        meson = self._configure_meson()
        meson.build()

    def package(self):
        files.copy(self, "COPYING", self.source_folder, "licenses")
        meson = self._configure_meson()
        meson.install()

        if microsoft.is_msvc(self) and not self.options.shared:
            files.rename(self, os.path.join(self.package_folder, "lib", "libgdk_pixbuf-2.0.a"), os.path.join(self.package_folder, "lib", "gdk_pixbuf-2.0.lib"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        files.rmdir(self, os.path.join(self.package_folder, "share"))
        files.rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "gdk-pixbuf-2.0")
        self.cpp_info.libs = ["gdk_pixbuf-2.0"]
        self.cpp_info.includedirs = [os.path.join("include", "gdk-pixbuf-2.0")]
        if not self.options.shared:
            self.cpp_info.defines.append("GDK_PIXBUF_STATIC_COMPILATION")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        if self._requires_compiler_rt:
            ldflags = ["-rtlib=compiler-rt"]
            self.cpp_info.exelinkflags = ldflags
            self.cpp_info.sharedlinkflags = ldflags

        gdk_pixbuf_pixdata = os.path.join(self.package_folder, "bin", "gdk-pixbuf-pixdata")
        self.runenv_info.define_path("GDK_PIXBUF_PIXDATA", gdk_pixbuf_pixdata)
        self.env_info.GDK_PIXBUF_PIXDATA = gdk_pixbuf_pixdata # remove in conan v2?

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "gdk-pixbuf-2.0"

    def package_id(self):
        if not self.options["glib"].shared:
            self.info.requires["glib"].full_package_mode()
