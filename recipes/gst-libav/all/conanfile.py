import glob
import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, msvc_runtime_flag
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class GStLibAVConan(ConanFile):
    name = "gst-libav"
    description = "GStreamer is a development framework for creating applications like media players, video editors, streaming media broadcasters and so on"
    license = "GPL-2.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gstreamer.freedesktop.org/"
    topics = ("gstreamer", "multimedia", "video", "audio", "broadcasting", "framework", "media")

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
        self.requires("glib/2.78.3")
        self.requires(f"gstreamer/{self.version}")
        self.requires(f"gst-plugins-base/{self.version}")
        self.requires("ffmpeg/7.0.1")

    def validate(self):
        if (
            self.options.shared != self.dependencies["gstreamer"].options.shared
            or self.options.shared != self.dependencies["glib"].options.shared
            or self.options.shared != self.dependencies["gst-plugins-base"].options.shared
        ):
            # https://gitlab.freedesktop.org/gstreamer/gst-build/-/issues/133
            raise ConanInvalidConfiguration("GLib, GStreamer and GstPlugins must be either all shared, or all static")
        if Version(self.version) >= "1.18.2" and self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(f"gst-plugins-good {self.version} does not support gcc older than 5")
        if self.options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("shared build with static runtime is not supported due to the FlsAlloc limit")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.settings.os == "Windows":
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("bison/3.8.2")
            self.tool_requires("flex/2.6.4")
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/1.78.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        def add_compiler_flag(value):
            tc.c_args.append(value)
            tc.cpp_args.append(value)

        def add_linker_flag(value):
            tc.c_link_args.append(value)
            tc.cpp_link_args.append(value)

        tc = MesonToolchain(self)
        if is_msvc(self):
            add_linker_flag("-lws2_32")
            add_compiler_flag(f"-{msvc_runtime_flag(self)}")
            if int(str(self.settings.compiler.version)) < 14:
                add_compiler_flag("-Dsnprintf=_snprintf")
        if msvc_runtime_flag(self):
            tc.project_options["b_vscrt"] = msvc_runtime_flag(self).lower()
        tc.project_options["tools"] = "disabled"
        tc.project_options["examples"] = "disabled"
        tc.project_options["benchmarks"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["wrap_mode"] = "nofallback"
        tc.project_options["introspection"] = "enabled" if self.options.with_introspection else "disabled"
        tc.generate()

        tc = PkgConfigDeps(self)
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
                    shutil.move(filename_old, filename_new)

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()
        self._fix_library_names(os.path.join(self.package_folder, "lib"))
        self._fix_library_names(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "gstreamer-1.0", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        plugins = ["libav"]

        gst_plugin_path = os.path.join(self.package_folder, "lib", "gstreamer-1.0")
        if self.options.shared:
            self.output.info(f"Appending GST_PLUGIN_PATH env var : {gst_plugin_path}")
            self.cpp_info.bindirs.append(gst_plugin_path)
            self.runenv_info.prepend_path("GST_PLUGIN_PATH", gst_plugin_path)
            self.env_info.GST_PLUGIN_PATH.append(gst_plugin_path)
        else:
            self.cpp_info.defines.append("GST_LIBAV_STATIC")
            self.cpp_info.libdirs.append(gst_plugin_path)
            self.cpp_info.libs.extend([f"gst{plugin}" for plugin in plugins])

        self.cpp_info.includedirs = ["include", os.path.join("include", "gstreamer-1.0")]
