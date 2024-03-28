import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"

backends = [
    "drm",
    "drm_screencast_vaapi",
    "headless",
    "pipewire",
    "rdp",
    "vnc",
    "wayland",
    "x11",
]
shells = ["desktop", "fullscreen", "ivi", "kiosk"]
simple_clients = [
    "damage",
    "im",
    "egl",
    "shm",
    "touch",
    "dmabuf_feedback",
    "dmabuf_v4l",
    "dmabuf_egl",
]
tools = ["calibrator", "debug", "info", "terminal", "touch-calibrator"]


class WestonConan(ConanFile):
    name = "weston"
    description = "Weston is a Wayland compositor designed for correctness, reliability, predictability, and performance."
    topics = ("compositor", "display", "kiosk", "wayland")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/wayland/weston"
    license = "MIT"
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "default_backend": backends,
        "demo_clients": [True, False],
        "desktop_shell_client_default": [None, "ANY"],
        "pipewire": [True, False],
        "remoting": [True, False],
        "renderer_gl": [True, False],
        "resize_pool": [True, False],
        "screenshare": [True, False],
        # "xwayland": [True, False],
        "wcap_decode": [True, False],
        "with_glib": [True, False],
        "with_lcms": [True, False],
        "with_libjpeg": [False, "libjpeg", "libjpeg-turbo"],
        "with_libudev": ["eudev", "systemd"],
        "with_libwebp": [True, False],
        "with_pam": [False, "openpam"],
        "with_systemd": [True, False],
    }
    options.update({f"backend_{backend}": [True, False] for backend in backends})
    options.update({f"shell_{shell}": [True, False] for shell in shells})
    options.update(
        {
            f"simple_client_{simple_client}": [True, False]
            for simple_client in simple_clients
        }
    )
    options.update({f"tool_{tool}": [True, False] for tool in tools})
    default_options = {
        "default_backend": "drm",
        "demo_clients": True,
        "desktop_shell_client_default": "weston-desktop-shell",
        "pipewire": True,
        "remoting": True,
        "renderer_gl": True,
        "resize_pool": True,
        "screenshare": True,
        # "xwayland": True,
        "wcap_decode": True,
        "with_glib": True,
        "with_lcms": True,
        "with_libjpeg": "libjpeg",
        "with_libwebp": True,
        "with_libudev": "systemd",
        "with_pam": "openpam",
        "with_systemd": True,
    }
    default_options.update({f"backend_{backend}": True for backend in backends})
    default_options.update({f"shell_{shell}": True for shell in shells})
    default_options.update(
        {f"simple_client_{simple_client}": True for simple_client in simple_clients}
    )
    default_options.update({f"tool_{tool}": True for tool in tools})
    # Unsupported due to missing Conan dependencies:
    default_options["backend_rdp"] = False
    default_options["backend_vnc"] = False
    default_options["remoting"] = False

    @property
    def _has_build_profile(self):
        return hasattr(self, "settings_build")

    @property
    def _requires_mesa_gbm(self):
        return self.options.backend_drm and self.options.renderer_gl

    @property
    def _requires_pam(self):
        return self.options.backend_vnc or self.options.get_safe("with_pam", True)

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

        if self.options.backend_drm and (
            self.options.remoting or self.options.pipewire
        ):
            self.options.renderer_gl = True

        if self.options.backend_drm and self.options.backend_drm_screencast_vaapi:
            self.options["libva"].with_drm = True

        if self._requires_mesa_gbm:
            self.options["mesa"].gbm = True

        if self.options.backend_vnc:
            self.options.rm_safe("with_pam")

        # if self.options.remoting:
        #     self.options["gstreamer"].good = True

        self.options["libglvnd"].egl = True
        self.options["libglvnd"].gles2 = True
        self.options["libinput"].with_libudev = self.options.with_libudev
        self.options["pango"].with_cairo = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cairo/1.18.0")
        self.requires("fontconfig/2.15.0")
        self.requires("libevdev/1.13.1")
        self.requires("libdrm/2.4.119")
        self.requires("libglvnd/1.7.0")
        self.requires("libinput/1.25.0")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("pixman/0.42.2", transitive_headers=True)
        self.requires("pango/1.51.0")
        self.requires("wayland/1.22.0", transitive_headers=True)
        self.requires("xkbcommon/1.6.0", transitive_headers=True)

        if self.options.with_glib:
            self.requires("glib/2.78.1")

        if self.options.backend_x11:
            self.requires("xorg/system")

        if self.options.with_libjpeg:
            if self.options.with_libjpeg == "libjpeg":
                self.requires("libjpeg/9e")
            elif self.options.with_libjpeg == "libjpeg-turbo":
                self.requires("libjpeg-turbo/3.0.2")

        if self.options.with_libwebp:
            self.requires("libwebp/1.3.2")

        if self.options.backend_pipewire or self.options.pipewire:
            self.requires("pipewire/1.0.4")

        # if self.options.backend_rdp:
        #     self.requires("freerdp/3.3.0")

        # if self.options.backend_vnc:
        #     self.requires("any1-aml/0.3.0")
        #     self.requires("neatvnc/0.8.0")

        if self.options.remoting:
            self.requires("gstreamer/1.22.6")

        if self._requires_pam and self.options.get_safe("with_pam") == "openpam":
            self.requires("openpam/20190224")

        if self.options.with_libudev == "systemd":
            self.requires("libudev/system")
        elif self.options.with_libudev == "eudev":
            self.requires("eudev/3.2.14")

        if self.options.backend_drm:
            self.requires("libdisplay-info/0.1.1")
            self.requires("libseat/0.8.0")
            # Requires mesa for libgbm
            if self.options.renderer_gl:
                self.requires("mesa/24.0.3")
            if self.options.backend_drm_screencast_vaapi:
                self.requires("libva/2.20.0")

        if self.options.with_lcms:
            self.requires("lcms/2.16")
        if self.options.with_systemd:
            self.requires("libsystemd/255.2")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")

        if not self.dependencies["pango"].options.with_cairo:
            raise ConanInvalidConfiguration(
                f"{self.name} requires the with_cairo option of the pango package to be enabled"
            )

        if self.options.simple_client_im and not self.options.with_glib:
            raise ConanInvalidConfiguration(
                "The simple_client_im option requires the with_glib option to be enabled"
            )

        if self.options.remoting and not self.options.with_glib:
            raise ConanInvalidConfiguration(
                "The remoting option requires the with_glib option to be enabled"
            )

        if self.options.renderer_gl and not self.dependencies["libglvnd"].options.egl:
            raise ConanInvalidConfiguration(
                "The renderer_gl option requires the egl option of the libglvnd package to be enabled"
            )

        if self.options.renderer_gl and not self.dependencies["libglvnd"].options.gles2:
            raise ConanInvalidConfiguration(
                "The renderer_gl option requires the gles2 option of the libglvnd package to be enabled"
            )

        if (
            self.options.backend_drm
            and self.options.renderer_gl
            and not self.dependencies["mesa"].options.gbm
        ):
            raise ConanInvalidConfiguration(
                f"{self.name} requires the gbm option of the mesa package to be enabled when the backend_drm and renderer_gl options are enabled"
            )

        if (
            self.options.backend_drm
            and (self.options.remoting or self.options.pipewire)
            and not self.options.renderer_gl
        ):
            raise ConanInvalidConfiguration(
                "The remoting and pipewire options require the renderer_gl option to be enabled"
            )

        if self.options.backend_drm and self.options.backend_drm_screencast_vaapi and not self.dependencies["libva"].options.with_drm:
            raise ConanInvalidConfiguration(
                f"{self.name} requires the with_drm option of the libva package to be enabled when the backend_drm and backend_drm_screencast_vaapi options are enabled"
            )

        # Unsupported due to missing Conan dependencies:
        if self.options.remoting:
            raise ConanInvalidConfiguration("The remoting option is not yet supported")
        if self.options.backend_rdp:
            raise ConanInvalidConfiguration(
                "The backend_rdp option is not yet supported. Contributions welcome."
            )
        if self.options.backend_vnc:
            raise ConanInvalidConfiguration(
                "The backend_vnc option is not yet supported. Contributions welcome."
            )

    def build_requirements(self):
        self.tool_requires("meson/1.3.2")
        if self._has_build_profile:
            self.tool_requires("wayland/<host_version>")
        self.tool_requires("wayland-protocols/1.33")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not self._has_build_profile:
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = MesonToolchain(self)
        tc.project_options["backend-default"] = str(self.options.default_backend)
        for backend in backends:
            unescaped_backend = backend.replace("_", "-")
            tc.project_options[f"backend-{unescaped_backend}"] = self.options.get_safe(
                f"backend_{backend}"
            )
        tc.project_options["build.pkg_config_path"] = self.generators_folder
        tc.project_options["color-management-lcms"] = self.options.with_lcms
        tc.project_options["datadir"] = os.path.join(self.package_folder, "res")
        tc.project_options["demo-clients"] = self.options.demo_clients
        tc.project_options["desktop-shell-client-default"] = str(
            self.options.desktop_shell_client_default
        )
        tc.project_options["doc"] = False
        if self.options.with_libjpeg:
            tc.project_options["image-jpeg"] = True
        tc.project_options["image-webp"] = self.options.with_libwebp
        tc.project_options["libexecdir"] = os.path.join(
            self.package_folder, "bin", "plugin"
        )
        tc.project_options["renderer-gl"] = self.options.renderer_gl
        tc.project_options["resize-pool"] = self.options.resize_pool
        tc.project_options["remoting"] = self.options.remoting
        tc.project_options["pipewire"] = self.options.pipewire
        tc.project_options["screenshare"] = self.options.screenshare
        for shell in shells:
            tc.project_options[f"shell-{shell}"] = self.options.get_safe(
                f"shell_{shell}"
            )
        tc.project_options["simple-clients"] = [
            simple_client.replace("_", "-")
            for simple_client in simple_clients
            if self.options.get_safe(f"simple_client_{simple_client}")
        ]
        tc.project_options["systemd"] = self.options.with_systemd
        tc.project_options["test-junit-xml"] = False
        tc.project_options["tools"] = [
            tool for tool in tools if self.options.get_safe(f"tools_{tool}")
        ]
        tc.project_options["wcap-decode"] = self.options.wcap_decode
        tc.project_options["xwayland"] = False
        tc.generate()

        pkg_config_deps = PkgConfigDeps(self)
        if self._has_build_profile:
            pkg_config_deps.build_context_activated = ["wayland", "wayland-protocols"]
            pkg_config_deps.build_context_suffix = {"wayland": "_BUILD"}
        else:
            # Manually generate pkgconfig file of wayland-protocols since
            # PkgConfigDeps.build_context_activated can't work with legacy 1 profile
            # We must use legacy conan v1 deps_cpp_info because self.dependencies doesn't
            # contain build requirements when using 1 profile.
            wp_prefix = self.deps_cpp_info["wayland-protocols"].rootpath
            wp_version = self.deps_cpp_info["wayland-protocols"].version
            wp_pkg_content = textwrap.dedent(
                f"""\
                prefix={wp_prefix}
                datarootdir=${{prefix}}/res
                pkgdatadir=${{datarootdir}}/wayland-protocols
                Name: Wayland Protocols
                Description: Wayland protocol files
                Version: {wp_version}
            """
            )
            save(
                self,
                os.path.join(self.generators_folder, "wayland-protocols.pc"),
                wp_pkg_content,
            )
        pkg_config_deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(
            self,
            os.path.join(self.source_folder, "meson.build"),
            "subdir('tests')",
            "#subdir('tests')",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, "meson.build"),
            "subdir('man')",
            "#subdir('man')",
        )
        if self._has_build_profile:
            # Patch the build system to use the pkg-config files generated for the build context.
            replace_in_file(
                self,
                os.path.join(self.source_folder, "protocol", "meson.build"),
                "dep_scanner = dependency('wayland-scanner', native: true)",
                "dep_scanner = dependency('wayland-scanner_BUILD', native: true)",
            )

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(
            self,
            "COPYING",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["weston"].libdirs = []
        self.cpp_info.components["weston"].includedirs = [
            os.path.join(self.package_folder, "include", "weston")
        ]
        self.cpp_info.components["weston"].set_property("pkg_config_name", "weston")
        pkg_config_variables = {
            "libexecdir": os.path.join(self.package_folder, "bin", "plugin"),
            "pkglibexecdir": "${libexecdir}/weston",
        }
        self.cpp_info.components["weston"].set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key, value in pkg_config_variables.items()),
        )
        self.cpp_info.components["weston"].requires = [
            "cairo::cairo_",
            "fontconfig::fontconfig",
            "glib::gobject-2.0",
            "libevdev::libevdev",
            "libinput::libinput",
            "libpng::libpng",
            "libweston",
            "pango::pangocairo",
            "pango::pango",
            "pixman::pixman",
            "wayland::wayland-cursor",
            "wayland::wayland-client",
            "wayland::wayland-server",
            "xkbcommon::libxkbcommon",
        ]
        if self.options.remoting:
            self.cpp_info.components["weston"].requires.extend(
                [
                    "gstreamer::gstreamer-1.0",
                    "gstreamer::gstreamer-allocators-1.0",
                    "gstreamer::gstreamer-app-1.0",
                    "gstreamer::gstreamer-video-1.0",
                    "glib::glib-2.0",
                ]
            )
        if self.options.backend_vnc:
            self.cpp_info.components["weston"].requires.append("openpam::openpam")
        if self.options.backend_x11:
            self.cpp_info.components["weston"].requires.append("xorg::xorg")
        if self.options.renderer_gl:
            self.cpp_info.components["weston"].requires.extend(
                ["libglvnd::egl", "libglvnd::gles2"]
            )
        if self.options.with_glib:
            self.cpp_info.components["weston"].requires.append("glib::gobject-2.0")
        if self.options.with_lcms:
            self.cpp_info.components["weston"].requires.append("lcms::lcms")
        if self.options.with_libjpeg == "libjpeg":
            self.cpp_info.components["weston"].requires.append("libjpeg::libjpeg")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.cpp_info.components["weston"].requires.append(
                "libjpeg-turbo::libjpeg-turbo"
            )
        if self.options.with_libudev == "systemd":
            self.cpp_info.components["weston"].requires.append("libudev::libudev")
        elif self.options.with_libudev == "eudev":
            self.cpp_info.components["weston"].requires.append("eudev::eudev")
        if self.options.with_libwebp:
            self.cpp_info.components["weston"].requires.append("libwebp::webp")
        if self.options.with_systemd:
            self.cpp_info.components["weston"].requires.append("libsystemd::libsystemd")
        self.cpp_info.components["weston"].system_libs = ["dl", "m", "pthread"]

        major_version = Version(self.version).major
        self.cpp_info.components["libweston"].set_property(
            "pkg_config_name", f"libweston-{major_version}"
        )
        self.cpp_info.components["libweston"].libs = [f"weston-{major_version}"]
        self.cpp_info.components["libweston"].includedirs = [
            os.path.join(self.package_folder, "include", f"libweston-{major_version}")
        ]
        self.cpp_info.components["libweston"].requires = [
            "libdrm::libdrm_libdrm",
            "pixman::pixman",
            "wayland::wayland-server",
            "xkbcommon::libxkbcommon",
        ]
        if self.options.backend_drm:
            self.cpp_info.components["libweston"].requires.extend(
                [
                    "libdisplay-info::libdisplay-info",
                    "libseat::libseat",
                ]
            )
            if self.options.backend_drm_screencast_vaapi:
                self.cpp_info.components["libweston"].requires.extend(["libva::libva_", "libva::libva-drm"])
        if self.options.backend_pipewire or self.options.pipewire:
            self.cpp_info.components["libweston"].requires.append("pipewire::libpipewire")
        if self.options.renderer_gl:
            self.cpp_info.components["libweston"].requires.extend(
                ["libglvnd::egl", "libglvnd::gles2"]
            )
        if self.options.with_lcms:
            self.cpp_info.components["libweston"].requires.append("lcms::lcms")
        if self.options.with_libudev == "systemd":
            self.cpp_info.components["libweston"].requires.append("libudev::libudev")
        elif self.options.with_libudev == "eudev":
            self.cpp_info.components["libweston"].requires.append("eudev::eudev")
        if self._requires_pam:
            self.cpp_info.components["libweston"].requires.append("openpam::openpam")
        if self._requires_mesa_gbm:
            self.cpp_info.components["libweston"].requires.append("mesa::gbm")
        self.cpp_info.components["libweston"].system_libs = ["dl", "m"]

        self.runenv_info.define_path("WESTON_DATA_DIR", os.path.join(self.package_folder, "res", "weston"))

        module_map = {}
        bin_dir = os.path.join(self.package_folder, "bin")
        weston_module_dir = os.path.join(self.package_folder, "lib", "weston")
        libweston_module_dir = os.path.join(self.package_folder, "lib", f"libweston-{major_version}")
        plugin_dir = os.path.join(self.package_folder, "bin", "plugin")

        if self.options.backend_drm:
            module_map["drm-backend.so"] = libweston_module_dir

        if self.options.backend_headless:
            module_map["headless-backend.so"] = libweston_module_dir

        if self.options.backend_pipewire:
            module_map["pipewire-backend.so"] = libweston_module_dir

        if self.options.backend_rdp:
            module_map["rdp-backend.so"] = libweston_module_dir

        if self.options.backend_vnc:
            module_map["vnc-backend.so"] = libweston_module_dir

        if self.options.backend_wayland:
            module_map["wayland-backend.so"] = libweston_module_dir

        if self.options.backend_x11:
            module_map["x11-backend.so"] = libweston_module_dir

        if self.options.with_lcms:
            module_map["color-lcms.so"] = libweston_module_dir

        if self.options.renderer_gl:
            module_map["gl-renderer.so"] = libweston_module_dir

        if self.options.pipewire:
            module_map["pipewire-plugin.so"] = libweston_module_dir

        if self.options.remoting:
            module_map["remoting-plugin.so"] = libweston_module_dir

        if self.options.shell_desktop:
            module_map["desktop-shell.so"] = weston_module_dir
            module_map["weston-desktop-shell"] = plugin_dir
            module_map["weston-keyboard"] = plugin_dir

        if self.options.shell_desktop or self.options.shell_fullscreen or self.options.shell_kiosk or self.options.shell_ivi:
            module_map["weston-screenshooter"] = bin_dir

        if self.options.shell_ivi:
            module_map["ivi-shell.so"] = weston_module_dir
            module_map["hmi-controller.so"] = weston_module_dir
            module_map["weston-ivi-shell-user-interface"] = plugin_dir

        if self.options.shell_kiosk:
            module_map["kiosk-shell.so"] = weston_module_dir

        if self.options.screenshare:
            module_map["screen-share.so"] = weston_module_dir

        if self.options.with_systemd:
            module_map["systemd-notify.so"] = weston_module_dir

        # if self.options.xwayland:
        #     module_map["xwayland.so"] = libweston_module_dir

        modules = str()
        for module, directory in module_map.items():
            modules += module + "=" + os.path.join(directory, module) + ";"

        self.runenv_info.prepend("WESTON_MODULE_MAP", modules)
