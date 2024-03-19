import glob
import os
import re
from io import StringIO

from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMakeDeps
from conan.tools.env import VirtualBuildEnv, Environment
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    load,
    get,
    replace_in_file,
    rm,
    rmdir,
    save,
)
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version


required_conan_version = ">=1.53.0"


# macOS:
#   https://docs.mesa3d.org/macos.html
#   https://github.com/Mesa3D/mesa/blob/main/.github/workflows/macos.yml
#   glx=dri has been broken since 23.0.0
#   Requires building under `brew sh` or will get errors about the include X11/Xlib.h not being found.

datasources = ["freedreno", "intel", "panfrost"]
freedreno_kmds = ["kgsl", "msm", "virtio"]
gallium_drivers = [
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
platforms = ["android", "haiku", "wayland", "windows", "x11"]
tools = [
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
video_codecs = ['av1dec', "av1enc", "h264dec", "h264enc", "h265dec", "h265enc", "vc1dec", "vp9dec"]
vulkan_drivers = [
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
vulkan_layers = [
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
        "draw_use_llvm": [True, False],
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
        "gallium_opencl": [False, "icd", "standalone"],
        "gallium_rusticl": [True, False],
        "gallium_va": [True, False],
        "gallium_vdpau": [True, False],
        "gallium_windows_dll_name": ["ANY"],
        "gallium_xa": [True, False],
        "gbm": [True, False],
        "gles1": [True, False],
        "gles2": [True, False],
        "glvnd_vendor_name": ["mesa"],
        "glx": [False, "dri", "xlib"],
        "glx_direct": [True, False],
        "imagination_srv": [True, False],
        "intel_clc": [True, False, "system"],
        "intel_xe_kmd": [True, False],
        "microsoft_clc": [True, False],
        "min_windows_version": ["7", "8", "10", "11"],
        "opencl_spirv": [True, False],
        "opengl": [True, False],
        "osmesa": [True, False],
        "platform_sdk_version": ["ANY"],
        "radv_build_id": [None, "ANY"],
        "shader_cache": [True, False],
        "shader_cache_default": [True, False],
        "shader_cache_max_size": [None, "ANY"],
        "shared_glapi": [True, False],
        "spirv_to_dxil": [True, False],
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
        "with_perfetto": [True, False],
        "with_zstd": [True, False],
        "with_zlib": [True, False],
        "xmlconfig": [True, False],
    }
    options.update(
        {f"datasource_{datasource}": [True, False] for datasource in datasources}
    )
    options.update(
        {
            f"freedreno_kmd_{freedreno_kmd}": [True, False]
            for freedreno_kmd in freedreno_kmds
        }
    )
    options.update(
        {
            f"gallium_driver_{gallium_driver}": [True, False]
            for gallium_driver in gallium_drivers
        }
    )
    options.update({f"platform_{platform}": [True, False] for platform in platforms})
    options.update({f"tool_{tool}": [True, False] for tool in tools})
    options.update(
        {f"video_codec_{video_codec}": [True, False] for video_codec in video_codecs}
    )
    options.update(
        {
            f"vulkan_driver_{vulkan_driver}": [True, False]
            for vulkan_driver in vulkan_drivers
        }
    )
    options.update(
        {
            f"vulkan_layer_{vulkan_layer}": [True, False]
            for vulkan_layer in vulkan_layers
        }
    )
    default_options = {
        "allow_kcmp": True,
        "android_stub": False,
        "android_libbacktrace": True,
        "draw_use_llvm": True,
        "dri3": True,
        "egl": True,
        "egl_lib_suffix": None,
        "egl_native_platform": "wayland",
        "gallium_d3d10umd": False,
        "gallium_d3d12_video": False,
        "gallium_extra_hud": False,
        "gallium_nine": False,
        "gallium_omx": False,
        "gallium_opencl": False,
        "gallium_rusticl": False,
        "gallium_va": True,
        "gallium_vdpau": True,
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
        "microsoft_clc": False,
        "min_windows_version": "8",
        "opencl_spirv": False,
        "opengl": True,
        "osmesa": False,
        "platform_sdk_version": "25",
        "radv_build_id": None,
        "spirv_to_dxil": False,
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
        # todo When the llvm Conan package is available, this should default to True.
        "with_llvm": False,
        # "with_lmsensors": True,
        "with_perfetto": False,
        "with_zlib": True,
        "with_zstd": True,
        "xmlconfig": True,
    }
    default_options.update(
        {f"datasource_{datasource}": False for datasource in datasources}
    )
    default_options.update(
        {
            f"freedreno_kmd_{freedreno_kmd}": freedreno_kmd == "msm"
            for freedreno_kmd in freedreno_kmds
        }
    )
    default_options.update(
        {
            f"gallium_driver_{gallium_driver}": False
            for gallium_driver in gallium_drivers
        }
    )
    default_options.update({f"platform_{platform}": True for platform in platforms})
    default_options.update({f"tool_{tool}": False for tool in tools})
    default_options.update(
        {f"video_codec_{video_codec}": False for video_codec in video_codecs}
    )
    default_options.update(
        {f"vulkan_driver_{vulkan_driver}": False for vulkan_driver in vulkan_drivers}
    )
    default_options.update(
        {f"vulkan_layer_{vulkan_layer}": True for vulkan_layer in vulkan_layers}
    )

    _env_pythonpath = Environment()

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _max_cppstd(self):
        return 17

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
        return self.options.get_safe("with_expat") or self.options.tool_intel or self.options.xmlconfig

    @property
    def _requires_moltenvk(self):
        return is_apple_os(self) and self.options.get_safe("gallium_driver_zink")

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
        for gallium_driver in gallium_drivers:
            if self.options.get_safe(f"gallium_driver_{gallium_driver}"):
                return True
        return False

    @property
    def _with_libdrm(self):
        return self.settings.os in ["Linux", "FreeBSD"]

    @property
    def _has_egl_option(self):
        return not is_apple_os(self)

    @property
    def _has_dri3_option(self):
        return self._system_has_kms_drm

    @property
    def _has_gbm_option(self):
        return self._system_has_kms_drm

    @property
    def _has_intel_clc_option(self):
        return self.settings.arch == "x86_64"

    @property
    def _has_microsoft_clc_option(self):
        return self.settings.os in ["Linux", "Windows"]

    @property
    def _has_min_windows_version_option(self):
        return self.settings.os == "Windows"

    @property
    def _has_platform_sdk_version_option(self):
        return self.settings.os == "Android"

    @property
    def _has_platform_android_option(self):
        return self.settings.os == "Android"

    @property
    def _has_platform_haiku_option(self):
        return False

    @property
    def _has_platform_wayland_option(self):
        return self._system_has_kms_drm

    @property
    def _has_platform_x11_option(self):
        return (
            self._system_has_kms_drm
            or self.settings.os == "Macos"
            or self.settings.get_safe("os.subsystem") == "cygwin"
        )

    @property
    def _has_platform_windows_option(self):
        return (
            self.settings.os == "Windows"
            and self.settings.get_safe("os.subsystem") is None
        )

    @property
    def _has_spirv_to_dxil_option(self):
        return True

    @property
    def _has_shader_cache_option(self):
        return self.settings.os != "Windows"

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
    def _has_xmlconfig_option(self):
        return self.settings.os not in ["Android", "Windows"]

    @property
    def _default_egl_option(self):
        return True

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
        # https://github.com/Mesa3D/mesa/actions/runs/4754558919
        # The GLX dri option on macOS no longer builds.
        elif self.settings.os == "Macos":
            return "xlib"
        return "dri"

    @property
    def _default_microsoft_clc_option(self):
        return False
        # todo Enable by default on Windows when the LLVM package is available.
        # return self.settings.os == "Windows"

    @property
    def _default_opencl_spirv_option(self):
        return (
            self.options.get_safe("gallium_opencl")
            or self.options.get_safe("gallium_rusticl")
            or self.options.get_safe("intel_clc")
            or self.options.get_safe("microsoft_clc")
        )

    @property
    def _default_shared_glapi_option(self):
        return True

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
            and (str(self.settings.arch).startswith("arm") or self.settings.arch in ["x86", "x86_64"]),
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
            "swrast": (self._system_has_kms_drm or self.settings.os == "Windows")
            and (
                self.settings.arch in ["mips", "mips64", "x86", "x86_64"]
                or str(self.settings.arch).startswith("arm")
            ),
            "virtio": False,
        }[option]

    @property
    def _default_vulkan_layer_device_select_option(self):
        return not (
            (
                self.settings.os == "Windows"
                and self.settings.get_safe("os.subsystem") is None
            )
            or self.settings.os == "Macos"
        )

    @property
    def _default_vulkan_layer_overlay_option(self):
        # Compilation error on Windows with MSVC?
        return not is_msvc(self)

    @property
    def _requires_libclc(self):
        return (
            self.options.get_safe("gallium_opencl")
            or self.options.get_safe("gallium_rusticl")
            or self.options.get_safe("intel_clc")
            or self.options.get_safe("microsoft_clc")
        )

    @property
    def _requires_llvm(self):
        return (
            self.options.get_safe("gallium_opencl")
            or self.options.get_safe("gallium_rusticl")
            or self.options.get_safe("intel_clc")
            or self.options.get_safe("microsoft_clc")
        )

    @property
    def _system_has_kms_drm(self):
        return self.settings.os in ["Android", "FreeBSD", "Linux", "SunOS"]

    @property
    def _with_any_gallium_driver(self):
        for gallium_driver in gallium_drivers:
            if self.options.get_safe(f"gallium_driver_{gallium_driver}"):
                return True
        return False

    @property
    def _with_any_opengl(self):
        return (
            self.options.get_safe("opengl")
            or self.options.get_safe("gles1")
            or self.options.get_safe("gles2")
        )

    @property
    def _with_any_vulkan_driver(self):
        for vulkan_driver in vulkan_drivers:
            if self.options.get_safe(f"vulkan_driver_{vulkan_driver}"):
                return True
        return False

    @property
    def _with_any_vulkan_layer(self):
        for vulkan_layer in vulkan_layers:
            if self.options.get_safe(f"vulkan_layer_{vulkan_layer}"):
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
        if not self._has_dri3_option:
            self.options.rm_safe("dri3")
        if not self._has_gbm_option:
            self.options.rm_safe("gbm")
        if not self._has_intel_clc_option:
            self.options.rm_safe("intel_clc")
        if not self._has_microsoft_clc_option:
            self.options.rm_safe("microsoft_clc")
        if not self._has_min_windows_version_option:
            self.options.rm_safe("min_windows_version")
        if not self._has_platform_sdk_version_option:
            self.options.rm_safe("platform_sdk_version")
        if not self._has_spirv_to_dxil_option:
            self.options.rm_safe("spirv_to_dxil")
        if not self._has_shader_cache_option:
            self.options.rm_safe("shader_cache")
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
        if not self._has_xmlconfig_option:
            self.options.rm_safe("xmlconfig")

        if not self._has_egl_option:
            self.options.rm_safe("egl")

        if self.settings.os != "Windows":
            self.options.rm_safe("gallium_windows_dll_name")
        else:
            self.options.rm_safe("gallium_vdpau")

        if not self._has_platform_android_option:
            self.options.rm_safe("platform_android")
        if not self._has_platform_haiku_option:
            self.options.rm_safe("platform_haiku")
        if not self._has_platform_wayland_option:
            self.options.rm_safe("platform_wayland")
        if not self._has_platform_windows_option:
            self.options.rm_safe("platform_windows")
        if not self._has_platform_x11_option:
            self.options.rm_safe("platform_x11")

        if is_apple_os(self):
            for vulkan_driver in vulkan_drivers:
                self.options.rm_safe(vulkan_driver)

        self.options.egl_native_platform = self._default_egl_native_platform_option

        self.options.gallium_driver_asahi = self._default_gallium_driver_option("asahi")
        self.options.gallium_driver_crocus = self._default_gallium_driver_option(
            "crocus"
        )
        self.options.gallium_driver_d3d12 = self._default_gallium_driver_option("d3d12")
        self.options.gallium_driver_etnaviv = self._default_gallium_driver_option(
            "etnaviv"
        )
        self.options.gallium_driver_freedreno = self._default_gallium_driver_option(
            "freedreno"
        )
        self.options.gallium_driver_i915 = self._default_gallium_driver_option("i915")
        self.options.gallium_driver_iris = self._default_gallium_driver_option("iris")
        self.options.gallium_driver_kmsro = self._default_gallium_driver_option("kmsro")
        self.options.gallium_driver_lima = self._default_gallium_driver_option("lima")
        self.options.gallium_driver_r300 = self._default_gallium_driver_option("r300")
        self.options.gallium_driver_r600 = self._default_gallium_driver_option("r600")
        self.options.gallium_driver_radeonsi = self._default_gallium_driver_option(
            "radeonsi"
        )
        self.options.gallium_driver_nouveau = self._default_gallium_driver_option(
            "nouveau"
        )
        self.options.gallium_driver_panfrost = self._default_gallium_driver_option(
            "panfrost"
        )
        self.options.gallium_driver_svga = self._default_gallium_driver_option("svga")
        self.options.gallium_driver_swrast = self._default_gallium_driver_option(
            "swrast"
        )
        self.options.gallium_driver_tegra = self._default_gallium_driver_option("tegra")
        self.options.gallium_driver_v3d = self._default_gallium_driver_option("v3d")
        self.options.gallium_driver_vc4 = self._default_gallium_driver_option("vc4")
        self.options.gallium_driver_virgl = self._default_gallium_driver_option("virgl")
        self.options.gallium_driver_zink = self._default_gallium_driver_option("zink")

        self.options.glx = self._default_glx_option

        self.options.microsoft_clc = self._default_microsoft_clc_option

        self.options.opencl_spirv = self._default_opencl_spirv_option

        self.options.vulkan_driver_amd = self._default_vulkan_driver_option("amd")
        self.options.vulkan_driver_broadcom = self._default_vulkan_driver_option(
            "broadcom"
        )
        self.options.vulkan_driver_freedreno = self._default_vulkan_driver_option(
            "freedreno"
        )
        self.options.vulkan_driver_imagination_experimental = (
            self._default_vulkan_driver_option("imagination_experimental")
        )
        self.options.vulkan_driver_intel = self._default_vulkan_driver_option("intel")
        self.options.vulkan_driver_intel_hasvk = self._default_vulkan_driver_option(
            "intel_hasvk"
        )
        self.options.vulkan_driver_microsoft_experimental = (
            self._default_vulkan_driver_option("microsoft_experimental")
        )
        self.options.vulkan_driver_nouveau_experimental = (
            self._default_vulkan_driver_option("nouveau_experimental")
        )
        self.options.vulkan_driver_panfrost = self._default_vulkan_driver_option(
            "panfrost"
        )
        self.options.vulkan_driver_swrast = self._default_vulkan_driver_option("swrast")
        self.options.vulkan_driver_virtio = self._default_vulkan_driver_option("virtio")

        self.options.vulkan_layer_device_select = (
            self._default_vulkan_layer_device_select_option
        )
        self.options.vulkan_layer_overlay = self._default_vulkan_layer_overlay_option

        # todo When the llvm Conan package is available, remove these two overrides to enable the options by default.
        self.options.gallium_driver_radeonsi = False
        self.options.vulkan_driver_swrast = False

    def configure(self):
        if self._has_with_libglvnd_option and not self.options.with_libglvnd:
            self.provides = "libglvnd"

        if not self.options.get_safe("shared_glapi"):
            self.options.rm_safe("egl")
            self.options.rm_safe("gles1")
            self.options.rm_safe("gles2")

        if self.options.get_safe("tool_intel") or self.options.get_safe("xmlconfig"):
            self.options.rm_safe("with_expat")

        if self.options.get_safe("with_libglvnd"):
            self.options.rm_safe("egl_lib_suffix")

        if not self.options.get_safe("with_llvm"):
            self.options.rm_safe("draw_use_llvm")

        if self.options.get_safe("egl") and self.options.get_safe("with_libglvnd"):
            self.options["libglvnd"].egl = True
        if (
            self.options.get_safe("vulkan_driver_amd")
            and not self.options.get_safe("platform_windows")
        ) or self.options.get_safe("gallium_driver_radeonsi"):
            self.options["libdrm"].amdgpu = True
        if self.options.get_safe("gallium_driver_i915"):
            self.options["libdrm"].intel = True
        if self.options.get_safe("gallium_driver_nouveau"):
            self.options["libdrm"].nouveau = True
        if (
            self.options.get_safe("gallium_driver_r300")
            or self.options.get_safe("gallium_driver_r600")
            or self.options.get_safe("gallium_driver_radeonsi")
        ):
            self.options["libdrm"].radeon = True
        if self.options.get_safe("gles1") and self.options.get_safe("with_libglvnd"):
            self.options["libglvnd"].gles1 = True
        if self.options.get_safe("gles2") and self.options.get_safe("with_libglvnd"):
            self.options["libglvnd"].gles2 = True
        if self.options.get_safe("glx") and self.options.get_safe("with_libglvnd"):
            self.options["libglvnd"].glx = True

        if self.options.get_safe("gallium_d3d12_video"):
            self.options.gallium_driver_d3d12 = True

        if (
            self.options.get_safe("gallium_rusticl")
            or self.options.get_safe("intel_clc")
            or self.options.get_safe("microsoft_clc")
        ):
            self.options.opencl_spirv = True

        if (
            self.options.get_safe("vulkan_driver_amd")
            or self.options.get_safe("vulkan_driver_intel")
            or self.options.get_safe("vulkan_layer_overlay")
        ):
            self.options["glslang"].build_executables = True
            self.options["glslang"].enable_optimizer = False

        if not self._with_gallium_drivers:
            self.options.rm_safe("gallium_va")
            self.options.rm_safe("gallium_vdpau")

        if not (
            self.options.get_safe("gallium_d3d12_video")
            or self.options.get_safe("gallium_driver_nouveau")
            or self.options.get_safe("gallium_driver_r600")
            or self.options.get_safe("gallium_driver_radeonsi")
            or self.options.get_safe("gallium_driver_virgl")
        ):
            self.options.rm_safe("gallium_va")

        # todo
        # if self._requires_libclc:
        #     self.dependencies["llvm"].options.with_project_libclc = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # todo not needed?
        # self.requires("libgettext/0.22")

        if self._with_libdrm:
            self.requires("libdrm/2.4.119")

        if self._requires_expat:
            self.requires("expat/2.6.0")

        if self.options.get_safe("platform_wayland"):
            self.requires("wayland/1.22.0")

        if self.options.get_safe("platform_x11"):
            self.requires("libxshmfence/1.3")
            if self.settings.os in ["FreeBSD", "Linux"]:
                self.requires("xorg/system")

        if self.options.with_libelf:
            self.requires("libelf/0.8.13")

        if self.options.get_safe("with_libglvnd"):
            self.requires("libglvnd/1.7.0")

        if self.options.get_safe("with_libselinux"):
            self.requires("libselinux/3.5")

        if self.options.get_safe("with_libudev") == "systemd":
            self.requires("libudev/system")
        elif self.options.get_safe("with_libudev") == "eudev":
            self.requires("eudev/3.2.14")

        if self.options.get_safe("with_libunwind"):
            self.requires("libunwind/1.7.2")

        if self.options.get_safe("with_llvm"):
            self.requires("llvm/17.0.2")

        if self.options.get_safe("opencl_spirv"):
            self.requires("spirv-tools/1.3.243.0")

        if self.options.get_safe("with_perfetto"):
            self.requires("perfetto/37.0")

        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")

        if self.options.with_zstd:
            self.requires("zstd/1.5.5")

        if (
            self.options.get_safe("gallium_driver_d3d12")
            or self.options.get_safe("gallium_d3d12_video")
            or self.options.get_safe("microsoft_clc")
            or self.options.get_safe("vulkan_driver_microsoft_experimental")
            or (
                self.settings.os == "Windows"
                and self.options.get_safe("gallium_driver_zink")
            )
            or (self.settings.os == "Windows" and self._with_any_vulkan_driver)
        ):
            self.requires("directx-headers/1.610.2")

        if self.options.get_safe("gallium_va"):
            self.requires("libva/2.20.0")

        if self.options.get_safe("gallium_vdpau"):
            self.requires("libvdpau/1.5")

        if self.options.get_safe("tool_freedreno"):
            self.requires("libarchive/3.7.2")
            self.requires("libxml2/2.11.4")
            self.requires("lua/5.4.6")

        if self._requires_moltenvk:
            self.requires("moltenvk/1.2.2")

    def validate(self):
        stdout = StringIO()
        python_suffix = ".exe" if self.settings.os == "Windows" else "3"
        if conan_version.major >= 2:
            self.run(f"python{python_suffix} --version", quiet=True, stdout=stdout)
        else:
            self.run(f"python{python_suffix} --version")
        python_version = stdout.getvalue().strip().replace("Python ", "")
        if Version(python_version) < "3.9":
            self.output.error(f"{self.ref} internal scripts require Python 3.9 or later. Please update your Python installation.")

        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)
            # todo Use check_max_cppstd from Conan V2.
            # check_max_cppstd(self, self._max_cppstd)
            if str(self.settings.compiler.cppstd) in ["20", "gnu20", "23", "gnu23"]:
                raise ConanInvalidConfiguration(
                    f"{self.ref} can not be built with the cppstd {self.settings.compiler.cppstd} which is later than maximum supported cppstd {self._max_cppstd}"
                )

        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False
        )
        if (
            minimum_version
            and Version(self.settings.compiler.version) < minimum_version
        ):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires at least version {minimum_version} of {self.settings.compiler}"
            )

        # todo Remove this when the llvm Conan package is merged.
        if self.options.get_safe(
            "with_llvm"
        ):
            raise ConanInvalidConfiguration(
                "The with_llvm option is not available until the llvm Conan package becomes available."
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

        if self.options.get_safe("gallium_d3d10umd") and not self.options.get_safe(
            "gallium_driver_swrast"
        ):
            raise ConanInvalidConfiguration(
                "The gallium_d3d10umd option requires the gallium_driver_swrast option to be enabled"
            )

        if self.options.get_safe("gallium_d3d12_video") and not self.options.get_safe(
            "gallium_driver_d3d12"
        ):
            raise ConanInvalidConfiguration(
                "The gallium_d3d12_video option requires the gallium_driver_d3d12 option to be enabled"
            )

        if (
            self.options.get_safe("gallium_driver_i915")
            and self._with_libdrm
            and not self.dependencies["libdrm"].options.intel
        ):
            raise ConanInvalidConfiguration(
                "The gallium_driver_i915 option requires the intel option of libdrm to be enabled"
            )

        if (
            self.options.get_safe("gallium_driver_nouveau")
            and self._with_libdrm
            and not self.dependencies["libdrm"].options.nouveau
        ):
            raise ConanInvalidConfiguration(
                "The gallium_driver_nouveau option requires the nouveau option of libdrm to be enabled"
            )

        if (
            (
                self.options.get_safe("gallium_driver_r300")
                or self.options.get_safe("gallium_driver_r600")
                or self.options.get_safe("gallium_driver_radeonsi")
            )
            and self._with_libdrm
            and not self.dependencies["libdrm"].options.radeon
        ):
            raise ConanInvalidConfiguration(
                "The gallium_driver_r300, gallium_driver_r600, and gallium_driver_radeonsi options require the radeon option of libdrm to be enabled"
            )

        if (
            self.options.get_safe("gallium_driver_radeonsi")
            or self.options.get_safe("vulkan_driver_swrast")
        ) and not self.options.get_safe("with_llvm"):
            raise ConanInvalidConfiguration(
                "The gallium_driver_radeonsi and vulkan_driver_swrast options require with_llvm to be enabled"
            )

        if self.options.get_safe("gallium_driver_tegra") and not self.options.get_safe(
            "gallium_driver_nouveau"
        ):
            raise ConanInvalidConfiguration(
                "The gallium_driver_tegra option requires the gallium_driver_nouveau option to be enabled"
            )

        if (
            (
                (
                    self.options.get_safe("vulkan_driver_amd")
                    and not self.options.get_safe("platform_windows")
                )
                or self.options.get_safe("gallium_driver_radeonsi")
            )
            and self._with_libdrm
            and not self.dependencies["libdrm"].options.amdgpu
        ):
            raise ConanInvalidConfiguration(
                "The vulkan_driver_amd option when not on Windows and gallium_driver_radeonsi option require the amdgpu option of libdrm to be enabled"
            )

        if (
            self.options.get_safe("gallium_opencl")
            and not self._with_any_gallium_driver
        ):
            raise ConanInvalidConfiguration(
                "The gallium_opencl option requires atleast one gallium driver to be enabled"
            )

        if self.options.get_safe("gallium_opencl") and not self.options.get_safe(
            "with_llvm"
        ):
            raise ConanInvalidConfiguration(
                "The gallium_opencl option requires the with_llvm option to be enabled"
            )

        if (
            self.options.get_safe("gallium_rusticl")
            and not self._with_any_gallium_driver
        ):
            raise ConanInvalidConfiguration(
                "The gallium_rusticl option requires atleast one gallium driver to be enabled"
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
            self.options.get_safe("platform_x11") and self._with_any_opengl
        ):
            raise ConanInvalidConfiguration(
                "The glx option requires platform_x11 and at least one OpenGL API option to be enabled"
            )

        if (
            self.options.get_safe("glx")
            and self.options.get_safe("with_libglvnd")
            and not self.dependencies["libglvnd"].options.glx
        ):
            raise ConanInvalidConfiguration(
                "The glx option requires the glx option of libglvnd to be enabled"
            )

        if (
            self.options.get_safe("gallium_rusticl")
            or self.options.get_safe("intel_clc")
            or self.options.get_safe("microsoft_clc")
        ) and not self.options.get_safe("opencl_spirv"):
            raise ConanInvalidConfiguration(
                "The gallium_rusticl, intel_clc, and microsoft_clc options require the opencl_spirv option to be enabled"
            )

        if self.options.get_safe("gallium_va") and self.settings.os == "Windows" and not self.dependencies.direct_host["libva"].options.with_win32:
            raise ConanInvalidConfiguration(
                "The gallium_va option requires the with_win32 option of the libva package to be enabled"
            )

        if self.options.get_safe("vmware_mks_stats") and not self.options.get_safe(
            "gallium_driver_svga"
        ):
            raise ConanInvalidConfiguration(
                "The vmware_mks_stats option requires the gallium_driver_svga option to be enabled"
            )

        if is_apple_os(self):
            for vulkan_driver in vulkan_drivers:
                if self.options.get_safe(f"vulkan_driver_{vulkan_driver}"):
                    raise ConanInvalidConfiguration(
                        f"Vulkan drivers are not supported on {self.settings.os}"
                    )

        if self.options.get_safe("vulkan_driver_swrast") and not self.options.get_safe(
            "gallium_driver_swrast"
        ):
            raise ConanInvalidConfiguration(
                "The vulkan_driver_swrast option requires the gallium_driver_swrast option to be enabled"
            )

        if self.options.get_safe("vulkan_layer_device_select") and (
            self.settings.os == "Windows"
            and self.settings.get_safe("os.subsystem") is None
        ):
            raise ConanInvalidConfiguration(
                "The vulkan_layer_device_select option requires unistd.h, which is not available on Windows when self.settings.os.subsystem is None"
            )

        if self.options.get_safe("vulkan_layer_overlay") and is_msvc(self):
            raise ConanInvalidConfiguration(
                "The vulkan_layer_overlay option doesn't compile with MSVC"
            )

        # todo
        # if self._requires_libclc and not (self.options.get_safe("with_llvm") and self.dependencies["llvm"].options.with_project_libclc):
        #     raise ConanInvalidConfiguration(
        #         "The gallium_opencl, gallium_rusticl, intel_clc, and microsoft_clc options require libclc from LLVM"
        #     )

        if self.options.get_safe("opencl_spirv") and not (
            self.options.get_safe("with_llvm")
            and self.dependencies.direct_host["llvm"].options.with_project_libclc
        ):
            raise ConanInvalidConfiguration(
                "The opencl_spirv option requires the with_project_libclc option to be enabled for the llvm package"
            )

    def build_requirements(self):
        self.tool_requires("meson/1.3.2")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        if self.options.get_safe("platform_wayland"):
            self.tool_requires("wayland/<host_version>")
            self.tool_requires("wayland-protocols/1.33")
        if self._settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("bison/3.8.2")
            self.tool_requires("flex/2.6.4")
        if (
            self.options.get_safe("vulkan_driver_amd")
            or self.options.get_safe("vulkan_driver_intel")
            or self.options.get_safe("vulkan_layer_overlay")
        ):
            self.tool_requires("glslang/11.7.0")
        # todo if self._requires_libclc and self.dependencies["llvm"].options.shared == False and self.options.with_zstd:
        # if self.options.get_safe("with_llvm"):
        #     self.tool_requires("llvm/<host_version>")
        if self._requires_libclc and self.options.with_zstd:
            self.tool_requires("zstd/<host_version>")

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(
            self,
            os.path.join(self.source_folder, "meson.build"),
            "dep_wl_scanner = dependency('wayland-scanner', native: true)",
            "dep_wl_scanner = dependency('wayland-scanner_BUILD', native: true)",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, "meson.build"),
            "dep_wl_protocols = dependency('wayland-protocols', version : '>= 1.30')",
            "dep_wl_protocols = dependency('wayland-protocols_BUILD', native: true, version : '>= 1.30')",
        )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        def boolean(option):
            return self.options.get_safe(option, default=False)
        def feature(option):
            return "enabled" if self.options.get_safe(option) else "disabled"

        def stringifier(option, default=""):
            return (
                str(self.options.get_safe(option))
                if self.options.get_safe(option)
                else default
            )

        tc = MesonToolchain(self)
        tc.project_options["android-stub"] = boolean("android_stub")
        tc.project_options["android-libbacktrace"] = feature("android_libbacktrace")
        tc.project_options["allow-kcmp"] = feature("allow_kcmp")
        tc.project_options["build-aco-tests"] = False
        tc.project_options["build-tests"] = False
        tc.project_options["datadir"] = os.path.join(self.package_folder, "res")
        tc.project_options["datasources"] = [
            datasource
            for datasource in datasources
            if self.options.get_safe(f"datasource_{datasource}")
        ]
        tc.project_options["draw-use-llvm"] = boolean("draw_use_llvm")
        tc.project_options["dri3"] = feature("dri3")
        tc.project_options["egl"] = feature("egl")
        tc.project_options["egl-lib-suffix"] = stringifier("egl_lib_suffix")
        tc.project_options["egl-native-platform"] = str(
            self.options.get_safe("egl_native_platform")
        )
        tc.project_options["enable-glcpp-tests"] = False
        tc.project_options["expat"] = "enabled" if self._requires_expat else "disabled"
        tc.project_options["freedreno-kmds"] = [
            freedreno_kmd
            for freedreno_kmd in freedreno_kmds
            if self.options.get_safe(f"freedreno_kmd_{freedreno_kmd}")
        ]
        tc.project_options["gallium-d3d10umd"] = boolean("gallium_d3d10umd")
        tc.project_options["gallium-d3d12-video"] = feature("gallium_d3d12_video")
        tc.project_options["gallium-drivers"] = [
            gallium_driver
            for gallium_driver in gallium_drivers
            if self.options.get_safe(f"gallium_driver_{gallium_driver}")
        ]
        tc.project_options["gallium-extra-hud"] = boolean("gallium_extra_hud")
        tc.project_options["gallium-nine"] = boolean("gallium_nine")
        tc.project_options["gallium-omx"] = stringifier("gallium_omx", default="disabled")
        tc.project_options["gallium-opencl"] = stringifier(
            "gallium_opencl", default="disabled"
        )
        tc.project_options["gallium-rusticl"] = boolean("gallium_rusticl")
        tc.project_options["gallium-va"] = feature("gallium_va")
        tc.project_options["gallium-vdpau"] = feature("gallium_vdpau")
        if self.options.get_safe("gallium_windows_dll_name"):
            tc.project_options["gallium-windows-dll-name"] = str(
                self.options.gallium_windows_dll_name
            )
        tc.project_options["gallium-xa"] = feature("gallium_xa")
        tc.project_options["gbm"] = feature("gbm")
        tc.project_options["gles1"] = feature("gles1")
        tc.project_options["gles2"] = feature("gles2")
        tc.project_options["glvnd"] = boolean("with_libglvnd")
        tc.project_options["glvnd-vendor-name"] = stringifier(
            "glvnd_vendor_name", default="mesa"
        )
        tc.project_options["glx"] = stringifier("glx", default="disabled")
        tc.project_options["glx-direct"] = boolean("glx_direct")
        tc.project_options["imagination-srv"] = boolean("imagination_srv")
        tc.project_options["install-intel-gpu-tests"] = False
        tc.project_options["intel-clc"] = (
            "system"
            if self.options.get_safe("intel_clc") == "system"
            else (feature("intel_clc"))
        )
        tc.project_options["intel-xe-kmd"] = feature("intel_xe_kmd")
        tc.project_options["llvm"] = feature("with_llvm")
        tc.project_options["libunwind"] = feature("with_libunwind")
        tc.project_options["microsoft-clc"] = feature("microsoft_clc")
        if self.options.get_safe("min_windows_version"):
            tc.project_options["min-windows-version"] = self.options.min_windows_version
        if self._requires_moltenvk:
            tc.project_options["moltenvk-dir"] = self.dependencies[
                "moltenvk"
            ].package_folder
        tc.project_options["opencl-spirv"] = boolean("opencl_spirv")
        tc.project_options["opengl"] = boolean("opengl")
        tc.project_options["osmesa"] = boolean("osmesa")
        tc.project_options["perfetto"] = boolean("with_perfetto")
        if self.options.get_safe("platform_sdk_version"):
            tc.project_options[
                "platform-sdk-version"
            ] = self.options.platform_sdk_version
        tc.project_options["platforms"] = [
            platform
            for platform in platforms
            if self.options.get_safe(f"platform_{platform}")
        ]
        tc.project_options["radv-build-id"] = stringifier("radv_build_id")
        tc.project_options["selinux"] = boolean("with_libselinux")
        tc.project_options["spirv-to-dxil"] = boolean("spirv_to_dxil")
        tc.project_options["shader-cache"] = feature("shader_cache")
        tc.project_options["shader-cache-default"] = boolean("shader_cache_default")
        tc.project_options["shader-cache-max-size"] = stringifier("shader_cache_max_size")
        tc.project_options["shared-glapi"] = feature("shared_glapi")
        if self.options.get_safe("with_llvm"):
            tc.project_options["shared-llvm"] = (
                "enabled" if self.dependencies["llvm"].options.shared else "disabled"
            )
        tc.project_options["sse2"] = boolean("sse2")
        tc.project_options["tools"] = [
            tool.replace("_", "-")
            for tool in tools
            if self.options.get_safe(f"tool_{tool}")
        ]
        tc.project_options["valgrind"] = "disabled"
        tc.project_options["video-codecs"] = [
            video_codec
            for video_codec in video_codecs
            if self.options.get_safe(f"video_codec_{video_codec}")
        ]
        tc.project_options["vmware-mks-stats"] = boolean("vmware_mks_stats")
        tc.project_options["vulkan-beta"] = boolean("vulkan_beta")
        tc.project_options["vulkan-drivers"] = [
            vulkan_driver.replace("_experimental", "-experimental")
            for vulkan_driver in vulkan_drivers
            if self.options.get_safe(f"vulkan_driver_{vulkan_driver}")
        ]
        tc.project_options["vulkan-layers"] = [
            vulkan_layer.replace("_", "-")
            for vulkan_layer in vulkan_layers
            if self.options.get_safe(f"vulkan_layer_{vulkan_layer}")
        ]
        tc.project_options["xmlconfig"] = feature("xmlconfig")
        tc.project_options["zlib"] = feature("with_zlib")
        tc.project_options["zstd"] = feature("with_zstd")
        if cross_building(self):
            tc.project_options["build.pkg_config_path"] = self.generators_folder
        tc.generate()
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.build_context_activated = ["wayland", "wayland-protocols"]
        pkg_config_deps.build_context_suffix = {"wayland": "_BUILD", "wayland-protocols": "_BUILD"}
        pkg_config_deps.generate()
        if self.options.get_safe("with_llvm"):
            cmake_deps = CMakeDeps(self)
            cmake_deps.generate()
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()

    def _install_python_mako(self):
        if self.conf.get("user.mesa:skip_install_mako", default=False, check_type=bool):
            return
        venv_folder = os.path.join(self.build_folder, "venv")
        script_subfolder = "Scripts" if self.settings.os == "Windows" else "bin"
        python_suffix = ".exe" if self.settings.os == "Windows" else "3"
        venv_python = os.path.join(venv_folder, script_subfolder, f"python{python_suffix}")
        self.run(f"python{python_suffix} -m venv {venv_folder}")
        self.run(f"{venv_python} -m pip install pip --upgrade")
        self.run(f"{venv_python} -m pip install mako==1.3.2")
        # INFO: Preserve user's PYTHONPATH in case defined. Only can access venv path after installing mako.
        pythonpath = None
        if self.settings.os == "Windows":
            pythonpath = glob.glob(os.path.join(self.build_folder, "venv", "lib", "python*", "site-packages"))
        else:
            pythonpath = os.path.join(self.build_folder, "venv", "Lib", "site-packages")
        self._env_pythonpath.append_path("PYTHONPATH", pythonpath)

    def build(self):
        self._install_python_mako()
        with self._env_pythonpath.vars(self).apply():
            meson = Meson(self)
            meson.configure()
            meson.build()

    def _extract_pkg_config_version(self, file):
        pkg_config = load(self, os.path.join(self.package_folder, "lib", "pkgconfig", file))
        return next(re.finditer("^Version: ([^\n$]+)[$\n]", pkg_config, flags=re.MULTILINE)).group(1)

    def _pkg_config_version_file(self, name):
        return os.path.join(self.package_folder, "res", f"{self.name}-{name}-version.txt")

    def _save_pkg_config_version(self, name):
        save(self, self._pkg_config_version_file(name), self._extract_pkg_config_version(f"{name}.pc"))

    def _load_pkg_config_version(self, name):
        load(self, self._pkg_config_version_file(name)).strip()

    def package(self):
        copy(
            self,
            "license.rst",
            os.path.join(self.source_folder, "docs"),
            os.path.join(self.package_folder, "licenses"),
        )
        with self._env_pythonpath.vars(self).apply():
            meson = Meson(self)
            meson.install()

        if self.options.get_safe("gallium_driver_d3d12"):
            self._save_pkg_config_version("d3d")
        if self.options.get_safe("osmesa"):
            self._save_pkg_config_version("osmesa")
        if self.options.get_safe("with_libglvnd") and self.options.get_safe("egl"):
            # According to the libglvnd ICD loading rules, an ICD library installed in a non-standard directory should be referenced using an absolute path.
            # For Conan, a relative path will have to suffice.
            replace_in_file(
                self,
                os.path.join(
                    self.package_folder, "res", "glvnd", "egl_vendor.d", "50_mesa.json"
                ),
                f"libEGL_{self.options.glvnd_vendor_name}",
                os.path.join(
                    "..",
                    "..",
                    "..",
                    "lib",
                    f"libEGL_{self.options.glvnd_vendor_name}",
                ),
            )

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

        fix_apple_shared_install_name(self)

    def package_info(self):
        if self.options.get_safe("gallium_driver_d3d12"):
            self.cpp_info.components["d3d"].set_property("pkg_config_name", "d3d")
            if self._with_libdrm:
                self.cpp_info.components["d3d"].requires.append("libdrm::libdrm")
            d3d_pkgconfig_variables = {
                # todo Use `libdir` when Conan V1 no longer needs to be supported.
                # 'moduledir': '${libdir}/d3d',
                'moduledir': '${prefix}/lib/d3d',
            }
            self.cpp_info.components["d3d"].set_property(
                "pkg_config_custom_content",
                "\n".join(f"{key}={value}" for key, value in d3d_pkgconfig_variables.items()))
            self.cpp_info.components["d3d"].set_property("component_version", str(self._load_pkg_config_version("d3d")))
        self.cpp_info.components["dri"].set_property("pkg_config_name", "dri")
        if self._with_libdrm:
            self.cpp_info.components["dri"].requires.append("libdrm::libdrm")
        self.cpp_info.components["dri"].set_property("component_version", self.version)
        dri_pkg_config_variables = {
            # todo Use `libdir` when Conan V1 no longer needs to be supported.
            # "dridriverdir": "${libdir}/dri",
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
            else:
                self.cpp_info.components["egl"].set_property("pkg_config_name", "egl")
            self.cpp_info.components["egl"].libs = [f"EGL{suffix}"]
            if self.options.get_safe("with_libglvnd"):
                self.cpp_info.components["egl"].requires.append("libglvnd::egl")
            if self.settings.os == "Windows":
                self.cpp_info.components["egl"].system_libs.append("opengl32")
        if self.options.get_safe("gbm"):
            self.cpp_info.components["gbm"].libs = ["gbm"]
            if self._requires_expat:
                self.cpp_info.components["gbm"].requires.append("expat::expat")
                self.cpp_info.components["gbm"].requires.append("libdrm::libdrm")
                self.cpp_info.components["gbm"].requires.append("wayland::wayland-server")
            self.cpp_info.components["gbm"].set_property("pkg_config_name", "gbm")
            self.cpp_info.components["gbm"].set_property(
                "component_version", self.version
            )
            gbm_pkg_config_variables = {
                # todo Use `libdir` when Conan V1 no longer needs to be supported.
                # "gbmbackendspath": "${libdir}/gbm",
                "gbmbackendspath": "${prefix}/lib/gbm",
            }
            self.cpp_info.components["gbm"].set_property(
                "pkg_config_custom_content",
                "\n".join(
                    f"{key}={value}" for key, value in gbm_pkg_config_variables.items()
                ),
            )
        if self.options.get_safe("gles1") and not self.options.get_safe("with_libglvnd"):
            self.cpp_info.components["gles1"].libs = ["GLESv1_CM"]
            self.cpp_info.components["gles1"].set_property("pkg_config_name", "glesv1_cm")
            if self.settings.os in ["FreeBSD", "Linux"]:
                self.cpp_info.components["gles1"].system_libs = ["m", "pthread"]
        if self.options.get_safe("gles2") and not self.options.get_safe("with_libglvnd"):
            self.cpp_info.components["gles2"].libs = ["GLESv2"]
            self.cpp_info.components["gles2"].set_property("pkg_config_name", "glesv1")
            if self.settings.os in ["FreeBSD", "Linux"]:
                self.cpp_info.components["gles2"].system_libs = ["m", "pthread"]
        if self.options.get_safe("glx"):
            glx_lib_name = (
                f"GLX_{self.options.glvnd_vendor_name}"
                if self.options.get_safe("with_libglvnd")
                else "GLX"
            )
            self.cpp_info.components["glx"].libs = [glx_lib_name]
            if self.options.get_safe("with_libglvnd"):
                self.cpp_info.components["glx"].requires.append("libglvnd::glx")

            gl_lib_name = (
                f"GLX_{self.options.glvnd_vendor_name}"
                if self.options.get_safe("with_libglvnd")
                else "GL"
            )
            self.cpp_info.components["gl"].libs = [gl_lib_name]
            if not self.options.get_safe("with_libglvnd"):
                gl_pkg_config_variables = {
                    "glx_tls": "yes",
                }
                self.cpp_info.components["gl"].set_property(
                    "pkg_config_custom_content",
                    "\n".join(
                        f"{key}={value}" for key, value in gl_pkg_config_variables.items()
                    ),
                )
                self.cpp_info.components["gl"].set_property("pkg_config_name", "gl")
            if self.options.get_safe("with_xorg"):
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
                self.cpp_info.components["glx"].requires.append("libxshmfence::libxshmfence")
                if self.options.get_safe("glx") == "dri":
                    self.cpp_info.components["gl"].requires.append("xorg::xxf86vm")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["gl"].system_libs.extend(["m", "pthread"])
            if self.settings.os == "Windows":
                self.cpp_info.components["gl"].system_libs.extend(["gdi32", "opengl32"])
        if self.options.get_safe("shared_glapi"):
            self.cpp_info.components["glapi"].libs = ["glapi"]
            if self.options.get_safe("with_libselinux"):
                self.cpp_info.components["glapi"].requires.append("libselinux::selinux")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["glapi"].system_libs.extend(["pthread"])
        if self.options.get_safe("osmesa"):
            self.cpp_info.components["osmesa"].libs = ["OSMesa"]
            self.cpp_info.components["osmesa"].set_property("pkg_config_name", "osmesa")
            self.cpp_info.components["osmesa"].set_property("component_version", str(self._load_pkg_config_version("osmesa")))
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.extend(["m", "pthread"])
            if self.options.get_safe("with_libselinux"):
                self.cpp_info.components["osmesa"].requires.append("libselinux::selinux")

        if self.settings.os == "Windows":
            self.cpp_info.components["gallium_wgl"].libs = [
                str(self.options.gallium_windows_dll_name)
            ]
            self.cpp_info.components["gallium_wgl"].system_libs.append("ws2_32")
            self.cpp_info.components["opengl32"].libs = ["opengl32"]
            self.cpp_info.components["opengl32"].requires = ["gallium_wgl"]
            self.cpp_info.components["opengl32"].system_libs.append("opengl32")

        if self.options.get_safe("with_expat") or self.options.get_safe("tool_intel") or self.options.get_safe("xmlconfig"):
            self.cpp_info.requires.append("expat::expat")

        if self.options.get_safe("platform_wayland"):
            self.cpp_info.requires.append("wayland::wayland")

        if self.options.get_safe("platform_x11"):
            self.cpp_info.requires.append("libxshmfence::libxshmfence")
            if self.settings.os in ["FreeBSD", "Linux"]:
                self.cpp_info.requires.append("xorg::xorg")

        if self.options.with_libelf:
            self.cpp_info.requires.append("libelf::libelf")

        if self.options.get_safe("with_libselinux"):
            self.cpp_info.requires.append("libselinux::selinux")

        if self.options.get_safe("with_libudev") == "systemd":
            self.cpp_info.requires.append("libudev::libudev")
        elif self.options.get_safe("with_libudev") == "eudev":
            self.cpp_info.requires.append("eudev::eudev")

        if self.options.get_safe("with_libunwind"):
            self.cpp_info.requires.append("libunwind::libunwind")

        if self.options.get_safe("opencl_spirv"):
            self.cpp_info.requires.append("spirv-tools::spirv-tools")

        if self.options.get_safe("with_perfetto"):
            self.cpp_info.requires.append("perfetto::perfetto")

        if self.options.with_zlib:
            self.cpp_info.requires.append("zlib::zlib")

        if self.options.with_zstd:
            self.cpp_info.requires.append("zstd::zstd")

        if self.options.get_safe("with_llvm"):
            self.cpp_info.requires.append("llvm::llvm")
        if self.options.get_safe("gallium_va"):
            self.cpp_info.requires.append("libva::libva_")
            if self.settings.os == "Windows":
                self.cpp_info.requires.append("libva::libva-win32")
        if self.options.get_safe("gallium_vdpau"):
            self.cpp_info.requires.append("libvdpau::libvdpau")

        if self.options.get_safe("tool_freedreno"):
            self.cpp_info.requires.append("libarchive::libarchive")
            self.cpp_info.requires.append("libxml2::libxml2")
            self.cpp_info.requires.append("lua::lua")

        if self._requires_moltenvk:
            self.cpp_info.requires.append("moltenvk::moltenvk")

        if (
            self.options.get_safe("gallium_driver_d3d12")
            or self.options.get_safe("gallium_d3d12_video")
            or self.options.get_safe("microsoft_clc")
            or self.options.get_safe("vulkan_driver_microsoft_experimental")
            or (
                self.settings.os == "Windows"
                and self.options.get_safe("gallium_driver_zink")
            )
            or (self.settings.os == "Windows" and self._with_any_vulkan_driver)
        ):
            self.cpp_info.requires.append("directx-headers::directx-headers")

        if self.options.get_safe("with_libglvnd") and self.options.get_safe("egl"):
            self.runenv_info.prepend_path("__EGL_VENDOR_LIBRARY_DIRS", os.path.join(self.package_folder, "res", "glvnd", "egl_vendor.d"))

        if self._with_gallium_drivers:
            libgl_drivers_path = os.path.join(self.package_folder, "lib", "dri")
            if self.settings.os == "Windows":
                libgl_drivers_path = os.path.join(self.package_folder, "bin")
            self.runenv_info.prepend_path("LIBGL_DRIVERS_PATH", libgl_drivers_path)

            if self.options.get_safe("gallium_va"):
                self.runenv_info.prepend_path("LIBVA_DRIVERS_PATH", libgl_drivers_path)

            if self.options.get_safe("gallium_vdpau"):
                self.runenv_info.prepend_path("VDPAU_DRIVER_PATH", os.path.join(self.package_folder, "lib", "vdpau"))

        if self.settings.os in ["FreeBSD", "Linux"]:
            self.runenv_info.prepend_path("DRIRC_CONFIGDIR", os.path.join(os.path.join(self.package_folder, "res", "drirc.d")))

        if self._with_any_vulkan_layer:
            self.runenv_info.prepend_path("VK_ADD_LAYER_PATH", os.path.join(self.package_folder, "res", "vulkan", "explicit_layer.d"))

        if self._with_any_vulkan_driver:
            for driver_file in glob.glob(os.path.join(self.package_folder, "res", "vulkan", "icd.d", "*.json")):
                self.runenv_info.prepend_path("VK_ADD_DRIVER_FILES", driver_file)
