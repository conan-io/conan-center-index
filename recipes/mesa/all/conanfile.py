from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    replace_in_file,
    rm,
    rmdir,
)
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"


# todo The Python mako module is required to build.
# macOS: https://github.com/Mesa3D/mesa/blob/main/.github/workflows/macos.yml

datasources_list = ["freedreno", "intel", "panfrost"]
freedreno_kmds_list = ["kgsl", "msm", "virtio"]
gallium_drivers_list = [
    "asahi",
    "crocus",
    "d3d12",
    "etnaviv",
    "freedreno",
    "i915",
    "iris",
    "kmsro",
    "lima",
    "r300",
    "r600",
    "radeonsi",
    "nouveau",
    "panfrost",
    "svga",
    "swrast",
    "tegra",
    "v3d",
    "vc4",
    "virgl",
    "zink",
]
platforms_list = ["android", "haiku", "wayland", "windows", "x11"]
tools_list = [
    "all",
    "asahi",
    "dlclose_skip",
    "drm-shim",
    "etnaviv",
    "freedreno",
    "glsl",
    "imagination",
    "intel",
    "intel-ui",
    "lima",
    "nir",
    "nouveau",
    "panfrost",
]
video_codecs_list = ["h264dec", "h264enc", "h265dec", "h265enc", "vc1dec"]
vulkan_drivers_list = [
    "amd",
    "broadcom",
    "freedreno",
    "imagination_experimental",
    "intel",
    "intel_hasvk",
    "microsoft_experimental",
    "nouveau_experimental",
    "panfrost",
    "swrast",
    "virtio",
]
vulkan_layers_list = [
    "device_select",
    "intel_nullhw",
    "overlay",
]


class MesaConan(ConanFile):
    name = "mesa"
    description = "An open-source implementation of various graphics APIs."
    # https://docs.mesa3d.org/license.html#mesa-component-licenses
    # Note: patent concerns for the codec support in Mesa
    license = ("MIT", "BSD-3-Clause", "SGI-B-2.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mesa3d.org/"
    topics = (
        "egl",
        "graphics",
        "opencl",
        "opengl",
        "opengles",
        "openmax",
        "va-api",
        "vdpau",
        "vulkan",
    )
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True
    # Reduce the cost of copying a lot of source code.
    no_copy_source = True
    options = {
        "android_stub": [True, False],
        "android_libbacktrace": [True, False],
        "allow_kcmp": [True, False],
        "dri3": [True, False],
        "egl": [True, False],
        "egl_lib_suffix": [None, "ANY"],
        "egl_native_platform": [
            "android",
            "drm",
            "haiku",
            "surfaceless",
            "wayland",
            "windows",
            "x11",
        ],
        "gallium_d3d10umd": [True, False],
        "gallium_d3d12_video": [True, False],
        "gallium_extra_hud": [True, False],
        "gallium_nine": [True, False],
        "gallium_omx": [False, "bellagio", "tizonia"],
        "gallium_va": [True, False],
        "gallium_vdpau": [True, False],
        "gallium_windows_dll_name": ["ANY"],
        "gallium_xa": [True, False],
        "gbm": [True, False],
        "gles1": [True, False],
        "gles2": [True, False],
        "glvnd_vendor_name": ["ANY"],
        "glx": [False, "dri", "xlib"],
        "glx_direct": [True, False],
        "imagination_srv": [True, False],
        "intel_clc": [True, False, "system"],
        "intel_xe_kmd": [True, False],
        "min_windows_version": ["7", "8", "10", "11"],
        "opengl": [True, False],
        "osmesa": [True, False],
        "perfetto": [True, False],
        "platform_sdk_version": ["ANY"],
        "radv_build_id": ["ANY"],
        "shader_cache": [True, False],
        "shader_cache_default": [True, False],
        "shader_cache_max_size": ["ANY"],
        "shared_glapi": [True, False],
        "sse2": [True, False],
        "vmware_mks_stats": [True, False],
        "vulkan_beta": [True, False],
        "with_expat": [True, False],
        "with_libelf": [True, False],
        "with_libglvnd": [True, False],
        "with_libselinux": [True, False],
        "with_libudev": ["eudev", "systemd"],
        "with_libunwind": [True, False],
        "with_llvm": [True, False],
        # "with_lmsensors": [True, False],
        "with_zstd": [True, False],
        "with_zlib": [True, False],
        "xmlconfig": [True, False],
    }
    options.update(
        {f"datasources_{datasource}": [True, False] for datasource in datasources_list}
    )
    options.update(
        {
            f"freedreno_kmds_{freedreno_kmd}": [True, False]
            for freedreno_kmd in freedreno_kmds_list
        }
    )
    options.update(
        {
            f"gallium_drivers_{gallium_driver}": [True, False]
            for gallium_driver in gallium_drivers_list
        }
    )
    options.update(
        {f"platforms_{platform}": [True, False] for platform in platforms_list}
    )
    options.update({f"tools_{tool}": [True, False] for tool in tools_list})
    options.update(
        {
            f"video_codecs_{video_codec}": [True, False]
            for video_codec in video_codecs_list
        }
    )
    options.update(
        {
            f"vulkan_drivers_{vulkan_driver}": [True, False]
            for vulkan_driver in vulkan_drivers_list
        }
    )
    options.update(
        {
            f"vulkan_layers_{vulkan_layer}": [True, False]
            for vulkan_layer in vulkan_layers_list
        }
    )
    default_options = {
        "allow_kcmp": True,
        "android_stub": False,
        "android_libbacktrace": True,
        "dri3": True,
        "egl": True,
        "egl_lib_suffix": None,
        "egl_native_platform": "wayland",
        "gallium_d3d10umd": False,
        "gallium_d3d12_video": False,
        "gallium_extra_hud": False,
        "gallium_nine": False,
        "gallium_omx": False,
        "gallium_va": False,
        "gallium_vdpau": False,
        "gallium_windows_dll_name": "libgallium_wgl",
        "gallium_xa": False,
        "gbm": True,
        "gles1": True,
        "gles2": True,
        "glvnd_vendor_name": "mesa",
        "glx": "dri",
        "glx_direct": True,
        "imagination_srv": False,
        "intel_clc": False,
        "intel_xe_kmd": False,
        "min_windows_version": "8",
        "opengl": True,
        "osmesa": False,
        "perfetto": False,
        "platform_sdk_version": "25",
        "radv_build_id": None,
        "shader_cache": True,
        "shader_cache_default": True,
        "shader_cache_max_size": None,
        "shared_glapi": True,
        "sse2": True,
        "vmware_mks_stats": False,
        "vulkan_beta": False,
        "with_expat": True,
        "with_libelf": True,
        "with_libglvnd": True,
        "with_libselinux": False,
        "with_libudev": "systemd",
        "with_libunwind": True,
        "with_llvm": True,
        # "with_lmsensors": True,
        "with_zlib": True,
        "with_zstd": True,
        "xmlconfig": True,
    }
    default_options.update(
        {f"datasources_{datasource}": False for datasource in datasources_list}
    )
    default_options.update(
        {
            f"freedreno_kmds_{freedreno_kmd}": freedreno_kmd == "msm"
            for freedreno_kmd in freedreno_kmds_list
        }
    )
    default_options.update(
        {
            f"gallium_drivers_{gallium_driver}": False
            for gallium_driver in gallium_drivers_list
        }
    )
    default_options.update(
        {f"platforms_{platform}": True for platform in platforms_list}
    )
    default_options.update({f"tools_{tool}": False for tool in tools_list})
    default_options.update(
        {f"video_codecs_{video_codec}": False for video_codec in video_codecs_list}
    )
    default_options.update(
        {
            f"vulkan_drivers_{vulkan_driver}": False
            for vulkan_driver in vulkan_drivers_list
        }
    )
    default_options.update(
        {f"vulkan_layers_{vulkan_layer}": True for vulkan_layer in vulkan_layers_list}
    )

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "13",
            "clang": "5",
            "gcc": "8",
            "msvc": "192",
            "Visual Studio": "16",
        }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _requires_expat(self):
        return self.options.get_safe("with_expat") or self.options.xmlconfig

    @property
    def _requires_moltenvk(self):
        return is_apple_os(self) and self.options.get_safe("gallium_drivers_zink")

    @property
    def _has_allow_kcmp_option(self):
        return self.settings.os == "Android"

    @property
    def _has_android_stub_option(self):
        return self.settings.os == "Android"

    @property
    def _has_android_libbacktrace_option(self):
        return self.settings.os == "Android"

    @property
    def _with_gallium_drivers(self):
        for gallium_driver in gallium_drivers_list:
            if self.options.get_safe(f"gallium_drivers_{gallium_driver}"):
                return True
        return False

    @property
    def _with_libdrm(self):
        return self.settings.os in ["Linux", "FreeBSD"]

    # @property
    # def _with_dri(self):
    #     return self.options.get_safe("glx") == "dri" or self.options.get_safe("egl")

    # @property
    # def _has_egl_option(self):
    #     return self._with_dri or self.settings.os in ["Android", "Windows"]

    @property
    def _has_gbm_option(self):
        return self._system_has_kms_drm

    @property
    def _has_min_windows_version_option(self):
        return self.settings.os == "Windows"

    @property
    def _has_platform_sdk_version_option(self):
        return self.settings.os == "Android"

    @property
    def _has_platforms_android_option(self):
        return self.settings.os == "Android"

    @property
    def _has_platforms_haiku_option(self):
        return False

    @property
    def _has_platforms_wayland_option(self):
        return self._system_has_kms_drm

    @property
    def _has_platforms_x11_option(self):
        return (
            self._system_has_kms_drm
            or self.settings.os == "Macos"
            or self.settings.get_safe("os.subsystem") == "cygwin"
        )

    @property
    def _has_platforms_windows_option(self):
        return (
            self.settings.os == "Windows"
            and self.settings.get_safe("os.subsystem") is None
        )

    @property
    def _has_with_libglvnd_option(self):
        return self.settings.os in ["FreeBSD", "Linux"]

    @property
    def _has_with_libselinux_option(self):
        return self.settings.os == "Linux"

    @property
    def _has_with_libudev_option(self):
        return self.settings.os == "Linux"

    @property
    def _has_with_libunwind_option(self):
        return self.settings.os in ["FreeBSD", "Linux"]

    @property
    def _has_shader_cache_option(self):
        return self.settings.os != "Windows"

    @property
    def _has_xmlconfig_option(self):
        return self.settings.os not in ["Android", "Windows"]

    @property
    def _default_egl_option(self):
        return True
        # return self.settings.os != "Windows"

    @property
    def _default_egl_native_platform_option(self):
        if self.settings.os == "Android":
            return "android"
        if self.settings.os == "Linux":
            return "wayland"
        if self._system_has_kms_drm:
            return "drm"
        if is_apple_os(self):
            return "surfaceless"
        if self.settings.os == "Windows":
            return "windows"

    @property
    def _default_glx_option(self):
        if self.settings.os in ["Android", "Windows"]:
            return False
        return "dri"

    @property
    def _default_shared_glapi_option(self):
        return True
        # return self.settings.os != "Windows"

    def _default_gallium_driver_option(self, option: str):
        return {
            "asahi": False,
            "crocus": self._system_has_kms_drm
            and self.settings.arch in ["x86", "x86_64"],
            "d3d12": False,
            "etnaviv": self._system_has_kms_drm
            and (str(self.settings.arch).startswith("arm")),
            "freedreno": self._system_has_kms_drm
            and str(self.settings.arch).startswith("arm"),
            "i915": self._system_has_kms_drm
            and self.settings.arch in ["x86", "x86_64"],
            "iris": self._system_has_kms_drm
            and str(self.settings.arch).startswith("arm"),
            # kmsro is enabled if any of the conditions for "asahi", "etnaviv", "freedreno", "lima", "panfrost", "v3d", or "vc4" are met.
            "kmsro": self._system_has_kms_drm
            and (str(self.settings.arch).startswith("arm")),
            "lima": self._system_has_kms_drm
            and str(self.settings.arch).startswith("arm"),
            "r300": self._system_has_kms_drm
            and self.settings.arch in ["mips", "mips64", "x86", "x86_64"],
            "r600": self._system_has_kms_drm
            and self.settings.arch in ["mips", "mips64", "x86", "x86_64"],
            "radeonsi": self._system_has_kms_drm
            and self.settings.arch in ["mips", "mips64", "x86", "x86_64"],
            "nouveau": self._system_has_kms_drm,
            "panfrost": self._system_has_kms_drm
            and str(self.settings.arch).startswith("arm"),
            "svga": self._system_has_kms_drm
            and (
                str(self.settings.arch).startswith("arm")
                or self.settings.arch in ["x86", "x86_64"]
            ),
            "swrast": is_apple_os(self)
            or self.settings.os == "Windows"
            or (
                self._system_has_kms_drm
                and self.settings.arch in ["mips", "mips64", "x86", "x86_64"]
            ),
            "tegra": self._system_has_kms_drm
            and str(self.settings.arch).startswith("arm"),
            "v3d": self._system_has_kms_drm
            and str(self.settings.arch).startswith("arm"),
            "vc4": self._system_has_kms_drm
            and str(self.settings.arch).startswith("arm"),
            "virgl": self._system_has_kms_drm,
            "zink": self.settings.os == "Macos",
        }[option]

    def _default_vulkan_driver_option(self, option: str):
        return {
            "amd": self._system_has_kms_drm
            and self.settings.arch in ["mips", "mips64", "x86", "x86_64"],
            "broadcom": False,
            "freedreno": False,
            "imagination_experimental": False,
            "intel": self._system_has_kms_drm
            and (
                self.settings.arch in ["x86", "x86_64"]
                or str(self.settings.arch).startswith("arm")
            ),
            "intel_hasvk": self._system_has_kms_drm
            and self.settings.arch in ["x86", "x86_64"],
            "microsoft_experimental": False,
            "nouveau_experimental": False,
            "panfrost": False,
            "swrast": True, # self._system_has_kms_drm todo Does this work on macOS?
            # and (
            #     self.settings.arch in ["mips", "mips64", "x86", "x86_64"]
            #     or str(self.settings.arch).startswith("arm")
            # ),
            "virtio": False,
        }[option]

    @property
    def _default_vulkan_layers_device_select_option(self):
        return not (self.settings.os == "Windows" and self.settings.get_safe("os.subsystem") is None)

    @property
    def _default_vulkan_layers_overlay_option(self):
        # Compilation error on Windows with MSVC?
        return not is_msvc(self)

    @property
    def _system_has_kms_drm(self):
        return self.settings.os in ["Android", "FreeBSD", "Linux", "SunOS"]

    @property
    def _with_any_opengl(self):
        return (
            self.options.get_safe("opengl")
            or self.options.get_safe("gles1")
            or self.options.get_safe("gles2")
        )

    @property
    def _with_any_vulkan_driver(self):
        for vulkan_driver in vulkan_drivers_list:
            if self.options.get_safe(f"vulkan_drivers_{vulkan_driver}"):
                return True
        return False

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if not self._has_allow_kcmp_option:
            self.options.rm_safe("allow_kcmp")
        if not self._has_android_stub_option:
            self.options.rm_safe("android_stub")
        if not self._has_android_libbacktrace_option:
            self.options.rm_safe("android_libbacktrace")
        if not self._has_gbm_option:
            self.options.rm_safe("gbm")
        if not self._has_min_windows_version_option:
            self.options.rm_safe("min_windows_version")
        if not self._has_platform_sdk_version_option:
            self.options.rm_safe("platform_sdk_version")
        if not self._has_with_libglvnd_option:
            self.options.rm_safe("with_libglvnd")
        else:
            self.options.rm_safe("egl_lib_suffix")
        if not self._has_with_libselinux_option:
            self.options.rm_safe("with_libselinux")
        if not self._has_with_libudev_option:
            self.options.rm_safe("with_libudev")
        if not self._has_with_libunwind_option:
            self.options.rm_safe("with_libunwind")
        if not self._has_shader_cache_option:
            self.options.rm_safe("shader_cache")
        if not self._has_xmlconfig_option:
            self.options.rm_safe("xmlconfig")

        if self.settings.os == "Macos":
            self.options.rm_safe("egl")

        if self.settings.os != "Windows":
            self.options.rm_safe("gallium_windows_dll_name")

        if not self._has_platforms_android_option:
            self.options.rm_safe("platforms_android")
        if not self._has_platforms_haiku_option:
            self.options.rm_safe("platforms_haiku")
        if not self._has_platforms_wayland_option:
            self.options.rm_safe("platforms_wayland")
        if not self._has_platforms_windows_option:
            self.options.rm_safe("platforms_windows")
        if not self._has_platforms_x11_option:
            self.options.rm_safe("platforms_x11")

        self.options.egl_native_platform = self._default_egl_native_platform_option

        self.options.gallium_drivers_asahi = self._default_gallium_driver_option(
            "asahi"
        )
        self.options.gallium_drivers_crocus = self._default_gallium_driver_option(
            "crocus"
        )
        self.options.gallium_drivers_d3d12 = self._default_gallium_driver_option(
            "d3d12"
        )
        self.options.gallium_drivers_etnaviv = self._default_gallium_driver_option(
            "etnaviv"
        )
        self.options.gallium_drivers_freedreno = self._default_gallium_driver_option(
            "freedreno"
        )
        self.options.gallium_drivers_i915 = self._default_gallium_driver_option("i915")
        self.options.gallium_drivers_iris = self._default_gallium_driver_option("iris")
        self.options.gallium_drivers_kmsro = self._default_gallium_driver_option(
            "kmsro"
        )
        self.options.gallium_drivers_lima = self._default_gallium_driver_option("lima")
        self.options.gallium_drivers_r300 = self._default_gallium_driver_option("r300")
        self.options.gallium_drivers_r600 = self._default_gallium_driver_option("r600")
        self.options.gallium_drivers_radeonsi = self._default_gallium_driver_option(
            "radeonsi"
        )
        self.options.gallium_drivers_nouveau = self._default_gallium_driver_option(
            "nouveau"
        )
        self.options.gallium_drivers_panfrost = self._default_gallium_driver_option(
            "panfrost"
        )
        self.options.gallium_drivers_svga = self._default_gallium_driver_option("svga")
        self.options.gallium_drivers_swrast = self._default_gallium_driver_option(
            "swrast"
        )
        self.options.gallium_drivers_tegra = self._default_gallium_driver_option(
            "tegra"
        )
        self.options.gallium_drivers_v3d = self._default_gallium_driver_option("v3d")
        self.options.gallium_drivers_vc4 = self._default_gallium_driver_option("vc4")
        self.options.gallium_drivers_virgl = self._default_gallium_driver_option(
            "virgl"
        )
        self.options.gallium_drivers_zink = self._default_gallium_driver_option("zink")

        self.options.glx = self._default_glx_option

        self.options.vulkan_drivers_amd = self._default_vulkan_driver_option("amd")
        self.options.vulkan_drivers_broadcom = self._default_vulkan_driver_option(
            "broadcom"
        )
        self.options.vulkan_drivers_freedreno = self._default_vulkan_driver_option(
            "freedreno"
        )
        self.options.vulkan_drivers_imagination_experimental = (
            self._default_vulkan_driver_option("imagination_experimental")
        )
        self.options.vulkan_drivers_intel = self._default_vulkan_driver_option("intel")
        self.options.vulkan_drivers_intel_hasvk = self._default_vulkan_driver_option(
            "intel_hasvk"
        )
        self.options.vulkan_drivers_microsoft_experimental = (
            self._default_vulkan_driver_option("microsoft_experimental")
        )
        self.options.vulkan_drivers_nouveau_experimental = (
            self._default_vulkan_driver_option("nouveau_experimental")
        )
        self.options.vulkan_drivers_panfrost = self._default_vulkan_driver_option(
            "panfrost"
        )
        self.options.vulkan_drivers_swrast = self._default_vulkan_driver_option(
            "swrast"
        )
        self.options.vulkan_drivers_virtio = self._default_vulkan_driver_option(
            "virtio"
        )
        self.options.vulkan_layers_device_select = self._default_vulkan_layers_device_select_option
        self.options.vulkan_layers_overlay = self._default_vulkan_layers_overlay_option

    def configure(self):
        if not self.options.get_safe("shared_glapi"):
            self.options.rm_safe("egl")
            self.options.rm_safe("gles1")
            self.options.rm_safe("gles2")

        if self.options.get_safe("xmlconfig"):
            self.options.rm_safe("with_expat")

        if self.options.get_safe("with_libglvnd"):
            self.options.rm_safe("egl_lib_suffix")

        if self.options.get_safe("egl"):
            self.options["libglvnd"].egl = True
        if (
            self.options.get_safe("vulkan_drivers_amd")
            and not self.options.get_safe("platforms_windows")
        ) or self.options.get_safe("gallium_drivers_radeonsi"):
            self.options["libdrm"].amdgpu = True
        if self.options.get_safe("gallium_drivers_i915"):
            self.options["libdrm"].intel = True
        if self.options.get_safe("gallium_drivers_nouveau"):
            self.options["libdrm"].nouveau = True
        if (
            self.options.get_safe("gallium_drivers_r300")
            or self.options.get_safe("gallium_drivers_r600")
            or self.options.get_safe("gallium_drivers_radeonsi")
        ):
            self.options["libdrm"].radeon = True
        if self.options.get_safe("gles1"):
            self.options["libglvnd"].gles1 = True
        if self.options.get_safe("gles2"):
            self.options["libglvnd"].gles2 = True
        if self.options.get_safe("glx"):
            self.options["libglvnd"].glx = True

        if self.options.get_safe("gallium_d3d12_video"):
            self.options.gallium_drivers_d3d12 = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libgettext/0.22")

        if self._with_libdrm:
            self.requires("libdrm/2.4.114")

        if self._requires_expat:
            self.requires("expat/2.5.0")

        if self.options.get_safe("platforms_wayland"):
            self.requires("wayland/1.22.0")
            self.requires("wayland-protocols/1.32")

        if self.options.get_safe("platforms_x11"):
            self.requires("libxshmfence/1.3")
            if self.settings.os in ["FreeBSD", "Linux"]:
                self.requires("xorg/system")

        if self.options.with_libelf:
            self.requires("libelf/0.8.13")

        if self.options.get_safe("with_libglvnd"):
            self.requires("libglvnd/1.5.0")

        if self.options.get_safe("with_libselinux"):
            self.requires("libselinux/3.5")

        if self.options.get_safe("with_libudev") == "systemd":
            self.requires("libsystemd/253.10")
        elif self.options.get_safe("with_libudev") == "eudev":
            self.requires("eudev/3.2.12")

        if self.options.get_safe("with_libunwind"):
            self.requires("libunwind/1.7.2")

        # todo Update this to use the new llvm package when it is merged.
        # if self.options.get_safe("with_llvm"):
            # self.requires("llvm-core/13.0.0")

        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")

        if self.options.with_zstd:
            self.requires("zstd/1.5.5")

        if (
            self.options.get_safe("gallium_drivers_d3d12")
            or self.options.get_safe("gallium_d3d12_video")
            or self.options.get_safe("vulkan_drivers_microsoft_experimental")
            or (self.settings.os == "Windows" and self.options.get_safe("gallium_drivers_zink"))
            or (self.settings.os == "Windows" and self._with_any_vulkan_driver)
        ):
            self.requires("directx-headers/1.610.2")

        if self.options.get_safe("tools_freedreno"):
            self.requires("libarchive/3.7.1")
            self.requires("libxml2/2.11.4")
            self.requires("lua/5.4.6")

        if self._requires_moltenvk:
            self.requires("moltenvk/1.2.2")

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires at least version {minimum_version} of {self.settings.compiler}"
            )

        if self.options.get_safe("egl") and not self.options.get_safe("shared_glapi"):
            raise ConanInvalidConfiguration(
                "The egl option requires the the shared_glapi option to be enabled"
            )

        if (
            self.options.get_safe("egl")
            and self.options.get_safe("with_libglvnd")
            and not self.dependencies["libglvnd"].options.egl
        ):
            raise ConanInvalidConfiguration(
                "The egl option requires the egl option of libglvnd to be enabled"
            )

        if self.options.get_safe("gallium_d3d12_video") and not self.options.get_safe(
            "gallium_drivers_d3d12"
        ):
            raise ConanInvalidConfiguration(
                "The gallium_d3d12_video option requires the gallium_drivers_d3d12 option to be enabled"
            )

        if self.options.get_safe(
            "gallium_drivers_d3d10umd"
        ) and not self.options.get_safe("gallium_drivers_swrast"):
            raise ConanInvalidConfiguration(
                "The gallium_drivers_d3d10umd option requires the gallium_drivers_swrast option to be enabled"
            )

        if (
            self.options.get_safe("gallium_drivers_i915")
            and self._with_libdrm
            and not self.dependencies["libdrm"].options.intel
        ):
            raise ConanInvalidConfiguration(
                "The gallium_drivers_i915 option requires the intel option of libdrm to be enabled"
            )

        if (
            self.options.get_safe("gallium_drivers_nouveau")
            and self._with_libdrm
            and not self.dependencies["libdrm"].options.nouveau
        ):
            raise ConanInvalidConfiguration(
                "The gallium_drivers_nouveau option requires the nouveau option of libdrm to be enabled"
            )

        if (
            (
                self.options.get_safe("gallium_drivers_r300")
                or self.options.get_safe("gallium_drivers_r600")
                or self.options.get_safe("gallium_drivers_radeonsi")
            )
            and self._with_libdrm
            and not self.dependencies["libdrm"].options.radeon
        ):
            raise ConanInvalidConfiguration(
                "The gallium_drivers_r300, gallium_drivers_r600, and gallium_drivers_radeonsi options require the radeon option of libdrm to be enabled"
            )

        if (
            self.options.get_safe("gallium_drivers_radeonsi")
            or self.options.get_safe("vulkan_drivers_swrast")
        ) and not self.options.get_safe("with_llvm"):
            raise ConanInvalidConfiguration(
                "The gallium_drivers_radeonsi and vulkan_drivers_swrast options require with_llvm to be enabled"
            )

        if self.options.get_safe("gallium_drivers_tegra") and not self.options.get_safe(
            "gallium_drivers_nouveau"
        ):
            raise ConanInvalidConfiguration(
                "The gallium_drivers_tegra option requires the gallium_drivers_nouveau option to be enabled"
            )

        if (
            (
                (
                    self.options.get_safe("vulkan_drivers_amd")
                    and not self.options.get_safe("platforms_windows")
                )
                or self.options.get_safe("gallium_drivers_radeonsi")
            )
            and self._with_libdrm
            and not self.dependencies["libdrm"].options.amdgpu
        ):
            raise ConanInvalidConfiguration(
                "The vulkan_drivers_amd option when not on Windows and gallium_drivers_radeonsi option require the amdgpu option of libdrm to be enabled"
            )

        if (
            self.options.get_safe("gles1")
            and self.options.get_safe("with_libglvnd")
            and not self.dependencies["libglvnd"].options.gles1
        ):
            raise ConanInvalidConfiguration(
                "The gles1 option requires the gles1 option of libglvnd to be enabled"
            )

        if (
            self.options.get_safe("gles2")
            and self.options.get_safe("with_libglvnd")
            and not self.dependencies["libglvnd"].options.gles2
        ):
            raise ConanInvalidConfiguration(
                "The gles2 option requires the gles2 option of libglvnd to be enabled"
            )

        if self.options.get_safe("glx") and not (
            self.options.get_safe("platforms_x11") and self._with_any_opengl
        ):
            raise ConanInvalidConfiguration(
                "The glx option requires platforms_x11 and at least one OpenGL API option to be enabled"
            )

        if (
            self.options.get_safe("glx")
            and self.options.get_safe("with_libglvnd")
            and not self.dependencies["libglvnd"].options.glx
        ):
            raise ConanInvalidConfiguration(
                "The glx option requires the glx option of libglvnd to be enabled"
            )

        # todo Does the swrast Vulkan driver work on macOS?
        # if self.settings.os == "Macos":
        #     for vulkan_driver in vulkan_drivers_list:
        #         if self.options.get_safe(f"vulkan_drivers_{vulkan_driver}"):
        #             raise ConanInvalidConfiguration(
        #                 "Vulkan is not supported on Macos or Windows yet"
        #             )

        if self.options.get_safe("vulkan_drivers_swrast") and not self.options.get_safe(
            "gallium_drivers_swrast"
        ):
            raise ConanInvalidConfiguration(
                "The vulkan_drivers_swrast option requires the gallium_drivers_swrast option to be enabled"
            )

        if self.options.get_safe("vulkan_layers_device_select") and (self.settings.os == "Windows" and self.settings.get_safe("os.subsystem") is None):
            raise ConanInvalidConfiguration(
                "The vulkan_layers_device_select option requires unistd.h, which is not available on Windows when self.settings.os.subsystem is None"
            )

        if self.options.get_safe("vulkan_layers_overlay") and is_msvc(self):
            raise ConanInvalidConfiguration(
                "The vulkan_layers_overlay option doesn't compile with MSVC"
            )


    def build_requirements(self):
        self.tool_requires("meson/1.2.2")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")
        if self.options.get_safe("platforms_wayland"):
            self.tool_requires("wayland/<host_version>")
        if self._settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.25")
            # todo Needed?
            # self.win_bash = True
            # if not self.conf.get("tools.microsoft.bash:path", check_type=str):
            #     self.tool_requires("msys2/cci.latest")
        else:
            self.tool_requires("bison/3.8.2")
            self.tool_requires("flex/2.6.4")
        if (
            self.options.get_safe("vulkan_drivers_amd")
            or self.options.get_safe("vulkan_drivers_intel")
            or self.options.get_safe("vulkan_layers_overlay")
        ):
            self.tool_requires("glslang/11.7.0")

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(
            self,
            os.path.join(self.source_folder, "meson.build"),
            "dep_wl_scanner = dependency('wayland-scanner', native: true)",
            "dep_wl_scanner = dependency('wayland-scanner_BUILD', native: true)",
        )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["android-stub"] = self.options.get_safe(
            "android_stub", default=False
        )
        tc.project_options["android-libbacktrace"] = (
            "enabled" if self.options.get_safe("android_libbacktrace") else "disabled"
        )
        tc.project_options["allow-kcmp"] = (
            "enabled" if self.options.get_safe("allow_kcmp") else "disabled"
        )
        tc.project_options["build-aco-tests"] = False
        tc.project_options["build-tests"] = False
        tc.project_options["datasources"] = [
            datasource
            for datasource in datasources_list
            if self.options.get_safe(f"datasources_{datasource}")
        ]
        tc.project_options["dri3"] = (
            "enabled" if self.options.get_safe("dri3") else "disabled"
        )
        tc.project_options["egl"] = (
            "enabled" if self.options.get_safe("egl") else "disabled"
        )
        tc.project_options["egl-lib-suffix"] = (
            str(self.options.egl_lib_suffix)
            if self.options.get_safe("egl_lib_suffix")
            else ""
        )
        tc.project_options["egl-native-platform"] = str(
            self.options.egl_native_platform
        )
        tc.project_options["enable-glcpp-tests"] = False
        tc.project_options["expat"] = "enabled" if self._requires_expat else "disabled"
        tc.project_options["freedreno-kmds"] = [
            freedreno_kmd
            for freedreno_kmd in freedreno_kmds_list
            if self.options.get_safe(f"freedreno_kmds_{freedreno_kmd}")
        ]
        tc.project_options["gallium-d3d10umd"] = self.options.get_safe(
            "gallium_d3d10umd", default=False
        )
        tc.project_options["gallium-d3d12-video"] = (
            "enabled" if self.options.get_safe("gallium_d3d12_video") else "disabled"
        )
        tc.project_options["gallium-drivers"] = [
            gallium_driver
            for gallium_driver in gallium_drivers_list
            if self.options.get_safe(f"gallium_drivers_{gallium_driver}")
        ]
        tc.project_options["gallium-extra-hud"] = self.options.get_safe(
            "gallium_extra_hud", default=False
        )
        tc.project_options["gallium-nine"] = self.options.get_safe(
            "gallium_nine", default=False
        )
        tc.project_options["gallium-omx"] = (
            "disabled"
            if not self.options.get_safe("gallium_omx")
            else str(self.options.get_safe("gallium_omx"))
        )
        tc.project_options["gallium-va"] = (
            "enabled" if self.options.get_safe("gallium_va") else "disabled"
        )
        tc.project_options["gallium-vdpau"] = (
            "enabled" if self.options.get_safe("gallium_vdpau") else "disabled"
        )
        if self.options.get_safe("gallium_windows_dll_name"):
            tc.project_options["gallium-windows-dll-name"] = str(
                self.options.gallium_windows_dll_name
            )
        tc.project_options["gallium-xa"] = (
            "enabled" if self.options.get_safe("gallium_xa") else "disabled"
        )
        tc.project_options["gbm"] = (
            "enabled" if self.options.get_safe("gbm") else "disabled"
        )
        tc.project_options["gles1"] = (
            "enabled" if self.options.get_safe("gles1") else "disabled"
        )
        tc.project_options["gles2"] = (
            "enabled" if self.options.get_safe("gles2") else "disabled"
        )
        if self.options.get_safe("with_libglvnd"):
            tc.project_options["glvnd"] = self.options.get_safe(
                "with_libglvnd", default=False
            )
        if self.options.get_safe("glvnd_vendor_name"):
            tc.project_options["glvnd-vendor-name"] = str(
                self.options.glvnd_vendor_name
            )
        tc.project_options["glx"] = (
            "disabled"
            if not self.options.get_safe("glx")
            else str(self.options.get_safe("glx"))
        )
        tc.project_options["glx-direct"] = self.options.get_safe(
            "glx_direct", default=True
        )
        tc.project_options["imagination-srv"] = self.options.get_safe(
            "imagination_srv", default=False
        )
        tc.project_options["install-intel-gpu-tests"] = False
        tc.project_options["intel-clc"] = (
            "system"
            if self.options.get_safe("intel_clc") == "system"
            else ("enabled" if self.options.get_safe("intel_clc") else "disabled")
        )
        tc.project_options["intel-xe-kmd"] = (
            "enabled" if self.options.get_safe("intel_xe_kmd") else "disabled"
        )
        tc.project_options["llvm"] = (
            "enabled" if self.options.get_safe("with_llvm") else "disabled"
        )
        tc.project_options["libunwind"] = (
            "enabled" if self.options.get_safe("with_libunwind") else "disabled"
        )
        if self.options.get_safe("min_windows_version"):
            tc.project_options["min-windows-version"] = self.options.min_windows_version
        if self._requires_moltenvk:
            tc.project_options["moltenvk-dir"] = self.dependencies["moltenvk"].package_folder
        tc.project_options["opengl"] = self.options.get_safe("opengl", default=False)
        tc.project_options["osmesa"] = self.options.get_safe("osmesa", default=False)
        tc.project_options["perfetto"] = self.options.get_safe(
            "perfetto", default=False
        )
        if self.options.get_safe("platform_sdk_version"):
            tc.project_options[
                "platform-sdk-version"
            ] = self.options.platform_sdk_version
        tc.project_options["platforms"] = [
            platform
            for platform in platforms_list
            if self.options.get_safe(f"platforms_{platform}")
        ]
        tc.project_options["radv-build-id"] = (
            str(self.options.radv_build_id) if self.options.radv_build_id else ""
        )
        tc.project_options["selinux"] = self.options.get_safe(
            "with_libselinux", default=False
        )
        tc.project_options["shader-cache"] = (
            "enabled" if self.options.get_safe("shader_cache") else "disabled"
        )
        tc.project_options["shader-cache-default"] = self.options.get_safe(
            "shader_cache_default", default=True
        )
        tc.project_options["shader-cache-max-size"] = (
            str(self.options.get_safe("shader_cache_max_size"))
            if self.options.get_safe("shader_cache_max_size")
            else ""
        )
        tc.project_options["shared-glapi"] = (
            "enabled" if self.options.get_safe("shared_glapi") else "disabled"
        )
        tc.project_options["sse2"] = self.options.get_safe("sse2", default=True)
        tc.project_options["tools"] = [
            tool.replace("_", "-")
            for tool in tools_list
            if self.options.get_safe(f"tools_{tool}")
        ]
        tc.project_options["valgrind"] = "disabled"
        tc.project_options["video-codecs"] = [
            video_codec
            for video_codec in video_codecs_list
            if self.options.get_safe(f"video_codecs_{video_codec}")
        ]
        tc.project_options["vmware-mks-stats"] = self.options.get_safe(
            "vmware_mks_stats", default=False
        )
        tc.project_options["vulkan-beta"] = self.options.get_safe(
            "vulkan_beta", default=False
        )
        tc.project_options["vulkan-drivers"] = [
            vulkan_driver.replace("_experimental", "-experimental")
            for vulkan_driver in vulkan_drivers_list
            if self.options.get_safe(f"vulkan_drivers_{vulkan_driver}")
        ]
        tc.project_options["vulkan-layers"] = [
            vulkan_layer.replace("_", "-")
            for vulkan_layer in vulkan_layers_list
            if self.options.get_safe(f"vulkan_layers_{vulkan_layer}")
        ]
        tc.project_options["xmlconfig"] = (
            "enabled" if self.options.get_safe("xmlconfig") else "disabled"
        )
        tc.project_options["zlib"] = "enabled" if self.options.with_zlib else "disabled"
        tc.project_options["zstd"] = "enabled" if self.options.with_zstd else "disabled"
        if cross_building(self):
            tc.project_options["build.pkg_config_path"] = self.generators_folder
        tc.generate()
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.build_context_activated = ["wayland"]
        pkg_config_deps.build_context_suffix = {"wayland": "_BUILD"}
        pkg_config_deps.generate()
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(
            self,
            "license.rst",
            os.path.join(self.source_folder, "docs"),
            os.path.join(self.package_folder, "licenses"),
        )
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

        fix_apple_shared_install_name(self)

    def package_info(self):
        if self.options.get_safe("gallium_drivers_d3d12"):
            self.cpp_info.components["d3d"].set_property("pkg_config_name", "d3d")
            if self._with_libdrm:
                self.cpp_info.components["d3d"].requires.append("libdrm::libdrm")
            # todo define pkg-config custom content for the `moduledir` variable
            # todo How to determine this?
            # self.cpp_info.components["d3d"].set_property("component_version", "1.0.0")
        self.cpp_info.components["dri"].set_property("pkg_config_name", "dri")
        if self._with_libdrm:
            self.cpp_info.components["dri"].requires.append("libdrm::libdrm")
        self.cpp_info.components["dri"].set_property("component_version", self.version)
        dri_pkg_config_variables = {
            # Can't use libdir here as it is libdir1 when using the PkgConfigDeps generator.
            "dridriverdir": "${prefix}/lib/dri",
        }
        self.cpp_info.components["dri"].set_property(
            "pkg_config_custom_content",
            "\n".join(
                f"{key}={value}" for key, value in dri_pkg_config_variables.items()
            ),
        )
        if self.options.get_safe("egl"):
            suffix = (
                self.options.egl_lib_suffix
                if self.options.get_safe("egl_lib_suffix")
                else ""
            )
            if self.options.get_safe("with_libglvnd"):
                suffix = f"_{self.options.glvnd_vendor_name}"
            self.cpp_info.components["egl"].libs = [f"EGL{suffix}"]
            if self.options.get_safe("with_libglvnd"):
                self.cpp_info.components["egl"].requires.append("libglvnd::egl")
            if self.settings.os == "Windows":
                self.cpp_info.components["egl"].system_libs.append("opengl32")
        if self.options.get_safe("gbm"):
            self.cpp_info.components["gbm"].libs = ["gbm"]
            self.cpp_info.components["gbm"].set_property("pkg_config_name", "gbm")
            self.cpp_info.components["gbm"].set_property(
                "component_version", self.version
            )
            gbm_pkg_config_variables = {
                # Can't use libdir here as it is libdir1 when using the PkgConfigDeps generator.
                "gbmbackendspath": "${prefix}/lib/gbm",
            }
            self.cpp_info.components["gbm"].set_property(
                "pkg_config_custom_content",
                "\n".join(
                    f"{key}={value}" for key, value in gbm_pkg_config_variables.items()
                ),
            )
        if self.options.get_safe("glx"):
            self.cpp_info.components["glx"].libs = ["GLX_mesa"]
            if self.options.get_safe("with_libglvnd"):
                self.cpp_info.components["glx"].requires.append("libglvnd::glx")
            gl_lib_name = (
                f"GLX_{self.options.glvnd_vendor_name}"
                if self.options.get_safe("with_libglvnd")
                else "GL"
            )
            self.cpp_info.components["gl"].libs = [gl_lib_name]
            if self.options.get_safe("with_xorg"):
                # todo Refine these more.
                self.cpp_info.components["gl"].requires.extend(
                    [
                        "xorg::x11",
                        "xorg::xcb",
                        "xorg::xcb-glx",
                        "xorg::xcb-shm",
                        "xorg::x11-xcb",
                        "xorg::xcb-dri2",
                        "xorg::xext",
                        "xorg::xfixes",
                    ]
                )
                if self.options.get_safe("with_glx") == "dri":
                    self.cpp_info.components["gl"].requires.append("xorg::xxf86vm")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["gl"].system_libs.extend(["m", "pthread"])
            if self.settings.os == "Windows":
                self.cpp_info.components["gl"].system_libs.extend(["gdi32", "opengl32"])
        if self.options.get_safe("shared_glapi"):
            self.cpp_info.components["glapi"].libs = ["glapi"]
        if self.options.get_safe("osmesa"):
            self.cpp_info.components["osmesa"].libs = ["OSMesa"]
            self.cpp_info.components["osmesa"].set_property("pkg_config_name", "osmesa")
            # self.cpp_info.components["osmesa"].set_property("component_version", "8.0.0")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.extend(["m", "pthread"])

        if self.settings.os == "Windows":
            self.cpp_info.components["gallium_wgl"].libs = [
                str(self.options.gallium_windows_dll_name)
            ]
            self.cpp_info.components["gallium_wgl"].system_libs.append("ws2_32")
            self.cpp_info.components["opengl32"].libs = ["opengl32"]
            self.cpp_info.components["opengl32"].requires = ["gallium_wgl"]
            self.cpp_info.components["opengl32"].system_libs.append("opengl32")

        libgl_drivers_path = os.path.join(self.package_folder, "lib", "dri")
        if self.settings.os == "Windows":
            libgl_drivers_path = os.path.join(self.package_folder, "bin")
        self.runenv_info.prepend_path("LIBGL_DRIVERS_PATH", libgl_drivers_path)
