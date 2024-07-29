from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rename, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, msvc_runtime_flag
from conan.tools.scm import Version
import os
import glob

required_conan_version = ">=1.56.0 <2 || >=2.0.6"


class AravisConan(ConanFile):
    name = "aravis"
    description = "A vision library for genicam based cameras."
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AravisProject/aravis"
    topics = ("usb", "camera")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "usb": [True, False],
        "packet_socket": [True, False],
        "gst_plugin": [True, False],
        "tools": [True, False],
        "introspection": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "usb": True,
        "packet_socket": True,
        "gst_plugin": False,
        "tools": True,
        "introspection": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.packet_socket

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if self.options.shared:
            self.options["glib"].shared = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # glib-object.h and gio/gio.h are used in several public headers
        self.requires("glib/2.78.3", transitive_headers=True)
        self.requires("libxml2/[>=2.12.5 <3]")
        self.requires("zlib/[>=1.2.11 <2]")

        if self.options.usb:
            self.requires("libusb/1.0.26")
        if self.options.gst_plugin:
            self.requires("gstreamer/1.22.3")
            self.requires("gst-plugins-base/1.19.2")

    def validate(self):
        if is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Static runtime is not supported on Windows due to GLib issues")
        if self.options.shared and not self.dependencies["glib"].options.shared:
            raise ConanInvalidConfiguration("Shared Aravis cannot link to static GLib")
        if is_apple_os(self) and self.dependencies["glib"].options.shared:
            raise ConanInvalidConfiguration(
                "macOS builds are disabled when glib is shared until "
                "conan-io/conan#7324 gets merged to fix macOS SIP issue #8443"
            )

    def build_requirements(self):
        #windows build: meson/1.2.1 works, meson/1.2.2 breaks for some reason!
        self.tool_requires("meson/1.4.0")
        self.tool_requires("glib/<host_version>")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        if self.options.introspection:
            self.tool_requires("gobject-introspection/1.72.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = MesonToolchain(self)
        tc.project_options["usb"] = "enabled" if self.options.usb else "disabled"
        tc.project_options["gst-plugin"] = "enabled" if self.options.gst_plugin else "disabled"
        tc.project_options["packet-socket"] = "enabled" if self.options.get_safe("packet_socket") else "disabled"
        tc.project_options["introspection"] = "enabled" if self.options.introspection else "disabled"
        tc.project_options["viewer"] = "disabled"
        tc.project_options["tests"] = False
        tc.project_options["documentation"] = "disabled"
        tc.project_options["fast-heartbeat"] = False
        if self.settings.get_safe("compiler.runtime"):
            tc.project_options["b_vscrt"] = msvc_runtime_flag(self).lower()
        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        meson = Meson(self)
        meson.configure()
        meson.build()

    def _fix_library_names(self, path):
        # https://github.com/mesonbuild/meson/issues/1412
        if not self.options.shared and is_msvc(self):
            with chdir(self, path):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info(f"rename {filename_old} into {filename_new}")
                    rename(self, filename_old, filename_new)

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        self._fix_library_names(os.path.join(self.package_folder, "lib"))
        if self.options.gst_plugin:
            self._fix_library_names(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        if not self.options.tools:
            rm(self, "arv-*", os.path.join(self.package_folder, "bin"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        version = Version(self.version)
        aravis_name = f"aravis-{version.major}.{version.minor}"
        self.cpp_info.set_property("pkg_config_name", aravis_name)
        self.cpp_info.includedirs = [os.path.join("include", aravis_name)]
        self.cpp_info.libs = [aravis_name]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread", "m", "resolv"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi"])

        if self.options.gst_plugin and self.options.shared:
            gst_plugin_path = os.path.join(self.package_folder, "lib", "gstreamer-1.0")
            self.runenv_info.prepend_path("GST_PLUGIN_PATH", gst_plugin_path)
            if self.options.tools:
                self.buildenv_info.prepend_path("GST_PLUGIN_PATH", gst_plugin_path)
            self.env_info.GST_PLUGIN_PATH.append(gst_plugin_path)
        if self.options.tools:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
