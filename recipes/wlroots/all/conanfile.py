import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rmdir, save
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain


required_conan_version = ">=1.53.0"


allocators = ["gbm"]
backends = ["drm", "libinput", "x11"]
renderers = ["gles2", "vulkan"]


class WlrootsConan(ConanFile):
    name = "wlroots"
    description = "Pluggable, composable, unopinionated modules for building a Wayland compositor; or about 60,000 lines of code you were going to write anyway."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/wlroots/wlroots"
    topics = ("compositor", "display", "graphics", "linux", "wayland")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "session": [True, False],
        "xwayland": [True, False],
    }
    options.update(
        {f"allocator_{allocator}": [True, False] for allocator in allocators}
    )
    options.update({f"backend_{backend}": [True, False] for backend in backends})
    options.update({f"renderer_{renderer}": [True, False] for renderer in renderers})
    default_options = {
        "shared": False,
        "fPIC": True,
        "session": True,
        # todo Enable this option by default when xwayland is available.
        "xwayland": False,
    }
    default_options.update({f"allocator_{allocator}": True for allocator in allocators})
    default_options.update({f"backend_{backend}": True for backend in backends})
    default_options.update({f"renderer_{renderer}": True for renderer in renderers})
    # todo When xcb-xinput is available in the xorg/system package, enable this option by default.
    default_options["backend_x11"] = False

    @property
    def _has_build_profile(self):
        return hasattr(self, "settings_build")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

        self.options["xkbcommon"].with_wayland = True

        if self.options.renderer_gles2:
            self.options["libglvnd"].egl = True
            self.options["libglvnd"].gles2 = True

        if self.options.allocator_gbm or self.options.renderer_gles2:
            self.options["mesa"].gbm = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libdrm/2.4.119")
        self.requires("pixman/0.43.0")
        self.requires("wayland/1.22.0")
        self.requires("xkbcommon/1.6.0")

        # For session support.
        if self.options.session:
            self.requires("libseat/0.8.0")
        self.requires("libudev/system")

        if self.options.allocator_gbm or self.options.renderer_gles2:
            self.requires("mesa/24.0.3")

        if self.options.backend_drm:
            self.requires("libdisplay-info/0.1.1")
            self.requires("libliftoff/0.4.1")

        if self.options.backend_libinput:
            self.requires("libinput/1.25.0")

        if self.options.renderer_gles2:
            self.requires("libglvnd/1.7.0")

        if self.options.renderer_vulkan:
            self.requires("vulkan-headers/1.3.268.0")
            self.requires("vulkan-loader/1.3.268.0")

        if self.options.backend_x11 or self.options.xwayland:
            self.requires("xorg/system")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.name} only supports Linux")
        if not self.dependencies["xkbcommon"].options.with_wayland:
            raise ConanInvalidConfiguration(
                f"{self.name} requires the with_wayland option of the xkbcommon package to be enabled"
            )
        if (
            self.options.allocator_gbm or self.options.renderer_gles2
        ) and not self.dependencies["mesa"].options.gbm:
            raise ConanInvalidConfiguration(
                f"{self.name} requires the gbm option of the mesa package to be enabled when the renderer_gles2 or allocator_gbm options are enabled"
            )
        if (
            self.options.renderer_gles2
            and not self.dependencies["libglvnd"].options.egl
        ):
            raise ConanInvalidConfiguration(
                f"{self.name} requires the egl option of the libglvnd package to be enabled when the renderer_gles2 option is enabled"
            )
        if (
            self.options.renderer_gles2
            and not self.dependencies["libglvnd"].options.gles2
        ):
            raise ConanInvalidConfiguration(
                f"{self.name} requires the gles2 option of the libglvnd package to be enabled when the renderer_gles2 option is enabled"
            )
        # todo Remove this check when xcb-xinput is available in the xorg/system package.
        if self.options.backend_x11:
            raise ConanInvalidConfiguration(
                f"{self.name} does not yet support the backend_x11 option. Contributions welcome."
            )
        # todo Remove this check when xwayland is available.
        if self.options.xwayland:
            raise ConanInvalidConfiguration(
                f"{self.name} does not yet support the xwayland option. Contributions welcome."
            )

    def build_requirements(self):
        self.tool_requires("meson/1.3.2")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        self.tool_requires("wayland/<host_version>")
        self.tool_requires("wayland-protocols/1.33")
        if self.options.backend_drm:
            self.tool_requires("hwdata/0.374")
        if self.options.renderer_vulkan:
            self.tool_requires("glslang/11.7.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["allocators"] = [
            allocator
            for allocator in allocators
            if self.options.get_safe(f"allocator_{allocator}")
        ]
        tc.project_options["backends"] = [
            backend
            for backend in backends
            if self.options.get_safe(f"backend_{backend}")
        ]
        tc.project_options["examples"] = False
        tc.project_options["renderers"] = [
            renderer
            for renderer in renderers
            if self.options.get_safe(f"renderer_{renderer}")
        ]
        tc.project_options["session"] = (
            "enabled" if self.options.session else "disabled"
        )
        tc.project_options["xcb-errors"] = "disabled"
        tc.project_options["xwayland"] = (
            "enabled" if self.options.xwayland else "disabled"
        )

        if self.options.allocator_gbm:
            tc.project_options["allocators"] = ["gbm"]

        tc.project_options["build.pkg_config_path"] = self.generators_folder
        tc.generate()

        pkg_config_deps = PkgConfigDeps(self)
        if self._has_build_profile:
            pkg_config_deps.build_context_activated = ["wayland", "wayland-protocols"]
            if self.options.backend_drm:
                pkg_config_deps.build_context_activated.append("hwdata")
            pkg_config_deps.build_context_suffix = {"wayland": "_BUILD"}
        else:
            # Manually generate pkgconfig file of wayland-protocols since
            # PkgConfigDeps.build_context_activated can't work with legacy 1 profile
            # We must use legacy conan v1 deps_cpp_info because self.dependencies doesn't
            # contain build requirements when using 1 profile.
            wp_prefix = self.deps_cpp_info["wayland-protocols"].rootpath
            wp_version = self.deps_cpp_info["wayland-protocols"].version
            wp_pkg_content = textwrap.dedent(f"""\
                prefix={wp_prefix}
                datarootdir=${{prefix}}/res
                pkgdatadir=${{datarootdir}}/wayland-protocols
                Name: Wayland Protocols
                Description: Wayland protocol files
                Version: {wp_version}
            """)
            save(
                self,
                os.path.join(self.generators_folder, "wayland-protocols.pc"),
                wp_pkg_content,
            )
        pkg_config_deps.generate()
        tc = VirtualBuildEnv(self)
        tc.generate()

    def _patch_sources(self):
        if self._has_build_profile:
            replace_in_file(
                self,
                os.path.join(self.source_folder, "protocol", "meson.build"),
                "wayland_scanner_dep = dependency('wayland-scanner', native: true)",
                "wayland_scanner_dep = dependency('wayland-scanner_BUILD', native: true)",
            )

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["wlroots"]
        self.cpp_info.requires = [
            "libdrm::libdrm",
            "libseat::libseat",
            "libudev::libudev",
            "pixman::pixman",
            "wayland::wayland-client",
            "wayland::wayland-server",
            "xkbcommon::libxkbcommon",
        ]
        if self.options.allocator_gbm or self.options.renderer_gles2:
            self.cpp_info.requires.append("mesa::gbm")
        if self.options.backend_drm:
            self.cpp_info.requires.append("libdisplay-info::libdisplay-info")
            self.cpp_info.requires.append("libliftoff::libliftoff")
        if self.options.backend_libinput:
            self.cpp_info.requires.append("libinput::libinput")
        if self.options.backend_x11:
            self.cpp_info.requires.extend(
                [
                    "xorg::xcb",
                    "xorg::xcb-dri3",
                    "xorg::xcb-present",
                    "xorg::xcb-render",
                    "xorg::xcb-renderutil",
                    "xorg::xcb-shm",
                    "xorg::xcb-xfixes",
                    "xorg::xcb-xinput",
                ]
            )
        if self.options.renderer_gles2:
            self.cpp_info.requires.append("libglvnd::egl")
            self.cpp_info.requires.append("libglvnd::gles2")
        if self.options.renderer_vulkan:
            self.cpp_info.requires.extend(
                [
                    "vulkan-loader::vulkan-loader",
                    "vulkan-headers::vulkan-headers",
                ]
            )
        if self.options.xwayland:
            self.cpp_info.requires.extend(
                [
                    "xorg::xcb",
                    "xorg::xcb-composite",
                    "xorg::xcb-ewmh",
                    "xorg::xcb-icccm",
                    "xorg::xcb-render",
                    "xorg::xcb-res",
                    "xorg::xcb-xfixes",
                ]
            )
        self.cpp_info.system_libs.extend(["m", "rt"])
        pkg_config_variables = {
            "have_xwayland": self.options.xwayland,
        }
        for allocator in allocators:
            pkg_config_variables.update(
                {
                    f"have_{allocator}_allocator": self.options.get_safe(
                        f"allocator_{allocator}"
                    )
                }
            )
        for backend in backends:
            pkg_config_variables.update(
                {f"have_{backend}_backend": self.options.get_safe(f"backend_{backend}")}
            )
        for renderer in renderers:
            pkg_config_variables.update(
                {
                    f"have_{renderer}_renderer": self.options.get_safe(
                        f"renderer_{renderer}"
                    )
                }
            )
        self.cpp_info.set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key, value in pkg_config_variables.items()),
        )
