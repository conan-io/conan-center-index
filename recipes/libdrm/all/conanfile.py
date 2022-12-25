import os
import re

from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration


class LibdrmConan(ConanFile):
    name = "libdrm"
    description = "User space library for accessing the Direct Rendering Manager, on operating systems that support the ioctl interface"
    topics = ("libdrm", "graphics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/mesa/drm"
    license = "MIT"
    generators = "PkgConfigDeps"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "libkms": [True, False],
        "intel": [True, False],
        "radeon": [True, False],
        "amdgpu": [True, False],
        "nouveau": [True, False],
        "vmwgfx": [True, False],
        "omap": [True, False],
        "exynos": [True, False],
        "freedreno": [True, False],
        "tegra": [True, False],
        "vc4": [True, False],
        "etnaviv": [True, False],
        "valgrind": [True, False],
        "freedreno-kgsl": [True, False],
        "udev": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "libkms": True,
        "intel": True,
        "radeon": True,
        "amdgpu": True,
        "nouveau": True,
        "vmwgfx": True,
        "omap": False,
        "exynos": False,
        "freedreno": True,
        "tegra": False,
        "vc4": True,
        "etnaviv": False,
        "valgrind": False,
        "freedreno-kgsl": False,
        "udev": False
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def build_requirements(self):
        self.build_requires("meson/0.59.0")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.intel:
            self.requires("libpciaccess/0.16")
        if self.settings.os == "Linux":
            self.requires("linux-headers-generic/5.14.9")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("libdrm supports only Linux or FreeBSD")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_meson(self):
        meson = Meson(self)

        defs={
            "cairo-tests" : "false",
            "install-test-programs": "false"
        }
        for o in ["libkms", "intel", "radeon", "amdgpu","nouveau", "vmwgfx", "omap", "exynos",
                  "freedreno", "tegra", "vc4", "etnaviv", "valgrind", "freedreno-kgsl", "udev"]:
            defs[o] = "true" if getattr(self.options, o) else "false"

        defs["datadir"] = os.path.join(self.package_folder, "res")
        defs["mandir"] = os.path.join(self.package_folder, "res", "man")

        meson.configure(
            defs = defs,
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder)
        return meson

    def build(self):
        meson = self._configure_meson()
        meson.build()

    def package(self):
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.mkdir(os.path.join(self.package_folder, "licenses"))
        # Extract the License/s from the header to a file
        tmp = tools.load(os.path.join(self._source_subfolder, "include", "drm", "drm.h"))
        license_contents = re.search("\*\/.*(\/\*(\*(?!\/)|[^*])*\*\/)", tmp, re.DOTALL)[1]
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package_info(self):
        self.cpp_info.components["libdrm_libdrm"].libs = ["drm"]
        self.cpp_info.components["libdrm_libdrm"].includedirs.append(os.path.join('include', 'libdrm'))
        self.cpp_info.components["libdrm_libdrm"].set_property("pkg_config_name", "libdrm")
        if self.settings.os == "Linux":
            self.cpp_info.components["libdrm_libdrm"].requires = ["linux-headers-generic::linux-headers-generic"]

        if self.options.libkms:
            self.cpp_info.components["libdrm_libkms"].libs = ["kms"]
            self.cpp_info.components["libdrm_libkms"].includedirs.append(os.path.join('include', 'libkms'))
            self.cpp_info.components["libdrm_libkms"].requires = ["libdrm_libdrm"]
            self.cpp_info.components["libdrm_libkms"].set_property("pkg_config_name", "libkms")

        if self.options.vc4:
            self.cpp_info.components["libdrm_vc4"].requires = ["libdrm_libdrm"]
            self.cpp_info.components["libdrm_vc4"].set_property("pkg_config_name", "libdrm_vc4")

        if self.options.freedreno:
            self.cpp_info.components["libdrm_freedreno"].libs = ["drm_freedreno"]
            self.cpp_info.components["libdrm_freedreno"].includedirs.append(os.path.join('include', 'libdrm'))
            self.cpp_info.components["libdrm_freedreno"].includedirs.append(os.path.join('include', 'freedreno'))
            self.cpp_info.components["libdrm_freedreno"].requires = ["libdrm_libdrm"]
            self.cpp_info.components["libdrm_freedreno"].set_property("pkg_config_name", "libdrm_freedreno")

        if self.options.amdgpu:
            self.cpp_info.components["libdrm_amdgpu"].libs = ["drm_amdgpu"]
            self.cpp_info.components["libdrm_amdgpu"].includedirs.append(os.path.join('include', 'libdrm'))
            self.cpp_info.components["libdrm_amdgpu"].requires = ["libdrm_libdrm"]
            self.cpp_info.components["libdrm_amdgpu"].set_property("pkg_config_name", "libdrm_amdgpu")

        if self.options.nouveau:
            self.cpp_info.components["libdrm_nouveau"].libs = ["drm_nouveau"]
            self.cpp_info.components["libdrm_nouveau"].includedirs.append(os.path.join('include', 'libdrm'))
            self.cpp_info.components["libdrm_nouveau"].requires = ["libdrm_libdrm"]
            self.cpp_info.components["libdrm_nouveau"].set_property("pkg_config_name", "libdrm_nouveau")

        if self.options.intel:
            self.cpp_info.components["libdrm_intel"].libs = ["drm_intel"]
            self.cpp_info.components["libdrm_intel"].includedirs.append(os.path.join('include', 'libdrm'))
            self.cpp_info.components["libdrm_intel"].requires = ["libdrm_libdrm", "libpciaccess::libpciaccess"]
            self.cpp_info.components["libdrm_intel"].set_property("pkg_config_name", "libdrm_intel")

        if self.options.radeon:
            self.cpp_info.components["libdrm_radeon"].libs = ["drm_radeon"]
            self.cpp_info.components["libdrm_radeon"].includedirs.append(os.path.join('include', 'libdrm'))
            self.cpp_info.components["libdrm_radeon"].requires = ["libdrm_libdrm"]
            self.cpp_info.components["libdrm_radeon"].set_property("pkg_config_name", "libdrm_radeon")

