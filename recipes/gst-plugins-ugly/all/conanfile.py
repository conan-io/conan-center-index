from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import chdir, copy, get, rename, rm, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, check_min_vs
from conan.tools.scm import Version

import glob
import os

required_conan_version = ">=1.60.0 <2 || >=2.0.5"


class GStPluginsUglyConan(ConanFile):
    name = "gst-plugins-ugly"
    description = "GStreamer is a development framework for creating applications like media players, video editors, " \
                  "streaming media broadcasters and so on"
    topics = ("gstreamer", "multimedia", "video", "audio", "broadcasting", "framework", "media")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gstreamer.freedesktop.org/"
    license = "GPL-2.0-only"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_introspection": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_introspection": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_legacy_one_profile(self):
        return not hasattr(self, "settings_build")

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
        self.options["gstreamer"].shared = self.options.shared
        self.options["gst-plugins-base"].shared = self.options.shared

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/2.78.3", transitive_headers=True, transitive_libs=True)
        self.requires("gstreamer/1.29.2", transitive_headers=True, transitive_libs=True)
        self.requires("gst-plugins-base/1.29.2", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.options.shared != self.dependencies.direct_host["gstreamer"].options.shared or \
           self.options.shared != self.dependencies.direct_host["glib"].options.shared or \
           self.options.shared != self.dependencies.direct_host["gst-plugins-base"].options.shared:
            # https://gitlab.freedesktop.org/gstreamer/gst-build/-/issues/133
            raise ConanInvalidConfiguration("GLib, GStreamer and GstPlugins must be either all shared, or all static")
        if Version(self.version) >= "1.18.2" and \
           self.settings.compiler == "gcc" and \
           Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(f"{self.ref} does not support gcc older than 5")
        if self.options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("shared build with static runtime is not supported due to the FlsAlloc limit")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self._is_legacy_one_profile:
            self.tool_requires("glib/<host_version>")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self._settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("bison/3.8.2")
            self.tool_requires("flex/2.6.4")
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/1.78.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        if self._is_legacy_one_profile:
            VirtualRunEnv(self).generate(scope="build")
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()
        tc = MesonToolchain(self)
        if is_msvc(self) and not check_min_vs(self, "190", raise_invalid=False):
            tc.c_args.append("-Dsnprintf=_snprintf")
            tc.project_options["c_std"] = "c99"
        if is_msvc(self):
            tc.c_link_args.append("-lws2_32")
            tc.cpp_link_args.append("-lws2_32")
        tc.project_options["tests"] = "disabled"
        tc.project_options["doc"] = "disabled"
        tc.project_options["wrap_mode"] = "nofallback"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        meson = Meson(self)
        meson.configure()
        meson.build()

    def _fix_library_names(self, path):
        # regression in 1.16
        if is_msvc(self):
            with chdir(self, path):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info(f"rename {filename_old} into {filename_new}")
                    rename(self, filename_old, filename_new)

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        self._fix_library_names(os.path.join(self.package_folder, "lib"))
        self._fix_library_names(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "gstreamer-1.0", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)

    @staticmethod
    def _installed_plugin_libs(gst_plugin_path, plugins):
        # The set of plugins actually built varies across gstreamer versions, so only
        # expose the ones whose static library was installed to avoid CMakeDeps errors.
        libs = []
        for plugin in plugins:
            lib = f"gst{plugin}"
            candidates = [f"lib{lib}.a", f"{lib}.lib", f"lib{lib}.so", f"lib{lib}.dylib", f"{lib}.dll"]
            if any(os.path.exists(os.path.join(gst_plugin_path, candidate)) for candidate in candidates):
                libs.append(lib)
        return libs

    def package_info(self):
        plugins = ["asf", "dvdlpcmdec", "dvdsub", "realmedia", "xingmux"]

        gst_plugin_path = os.path.join(self.package_folder, "lib", "gstreamer-1.0")
        if self.options.shared:
            self.runenv_info.append_path("GST_PLUGIN_PATH", gst_plugin_path)
            # TODO: remove the following when only Conan 2.0 is supported
            self.env_info.GST_PLUGIN_PATH.append(gst_plugin_path)
            self.cpp_info.bindirs.append(gst_plugin_path)
        else:
            self.cpp_info.defines.append("GST_PLUGINS_UGLY_STATIC")
            self.cpp_info.libdirs.append(gst_plugin_path)
            self.cpp_info.libs.extend(self._installed_plugin_libs(gst_plugin_path, plugins))

        self.cpp_info.includedirs = [
            includedir for includedir in ["include", os.path.join("include", "gstreamer-1.0")]
            if os.path.isdir(os.path.join(self.package_folder, includedir))
        ]
