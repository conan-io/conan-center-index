import os
import re

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, load, mkdir, rmdir, save
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LibdrmConan(ConanFile):
    name = "libdrm"
    description = ("User space library for accessing the Direct Rendering Manager, "
                   "on operating systems that support the ioctl interface")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/mesa/drm"
    topics = ("graphics",)

    package_type = "library"
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
        "udev": [True, False],
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
        "udev": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) >= "2.4.111":
            del self.options.libkms

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.intel:
            self.requires("libpciaccess/0.17")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("linux-headers-generic/6.5.9")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("libdrm supports only Linux or FreeBSD")

    def build_requirements(self):
        self.tool_requires("meson/1.3.0")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = PkgConfigDeps(self)
        tc.generate()

        tc = MesonToolchain(self)
        tc.project_options["cairo-tests"] = "disabled" if Version(self.version) >= "2.4.113" else "false"
        tc.project_options["install-test-programs"] = "false"

        if Version(self.version) < "2.4.111":
            tc.project_options["libkms"] = "true" if self.options.libkms else "false"

        tc.project_options["freedreno-kgsl"] = "true" if getattr(self.options, "freedreno-kgsl") else "false"
        tc.project_options["udev"] = "true" if self.options.udev else "false"

        for o in ["intel", "radeon", "amdgpu", "nouveau", "vmwgfx", "omap",
                  "exynos", "freedreno", "tegra", "vc4", "etnaviv", "valgrind"]:
            if Version(self.version) >= "2.4.113":
                tc.project_options[o] = "enabled" if getattr(self.options, o) else "disabled"
            else:
                tc.project_options[o] = "true" if getattr(self.options, o) else "false"

        tc.project_options["datadir"] = os.path.join(self.package_folder, "res")
        tc.project_options["mandir"] = os.path.join(self.package_folder, "res", "man")
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        mkdir(self, os.path.join(self.package_folder, "licenses"))
        # Extract the License/s from the header to a file
        tmp = load(self, os.path.join(self.source_folder, "include", "drm", "drm.h"))
        license_contents = re.search(r"\*/.*(/\*(\*(?!/)|[^*])*\*/)", tmp, re.DOTALL)[1]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package_info(self):
        self.cpp_info.components["libdrm_libdrm"].libs = ["drm"]
        self.cpp_info.components["libdrm_libdrm"].includedirs.append(os.path.join("include", "libdrm"))
        self.cpp_info.components["libdrm_libdrm"].set_property("pkg_config_name", "libdrm")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libdrm_libdrm"].requires = ["linux-headers-generic::linux-headers-generic"]

        if Version(self.version) < "2.4.111":
            if self.options.libkms:
                self.cpp_info.components["libdrm_libkms"].libs = ["kms"]
                self.cpp_info.components["libdrm_libkms"].includedirs.append(os.path.join("include", "libkms"))
                self.cpp_info.components["libdrm_libkms"].requires = ["libdrm_libdrm"]
                self.cpp_info.components["libdrm_libkms"].set_property("pkg_config_name", "libkms")

        if self.options.vc4:
            self.cpp_info.components["libdrm_vc4"].requires = ["libdrm_libdrm"]
            self.cpp_info.components["libdrm_vc4"].set_property("pkg_config_name", "libdrm_vc4")

        if self.options.freedreno:
            self.cpp_info.components["libdrm_freedreno"].libs = ["drm_freedreno"]
            self.cpp_info.components["libdrm_freedreno"].includedirs.append(os.path.join("include", "libdrm"))
            self.cpp_info.components["libdrm_freedreno"].includedirs.append(os.path.join("include", "freedreno"))
            self.cpp_info.components["libdrm_freedreno"].requires = ["libdrm_libdrm"]
            self.cpp_info.components["libdrm_freedreno"].set_property("pkg_config_name", "libdrm_freedreno")

        if self.options.amdgpu:
            self.cpp_info.components["libdrm_amdgpu"].libs = ["drm_amdgpu"]
            self.cpp_info.components["libdrm_amdgpu"].includedirs.append(os.path.join("include", "libdrm"))
            self.cpp_info.components["libdrm_amdgpu"].requires = ["libdrm_libdrm"]
            self.cpp_info.components["libdrm_amdgpu"].set_property("pkg_config_name", "libdrm_amdgpu")

        if self.options.nouveau:
            self.cpp_info.components["libdrm_nouveau"].libs = ["drm_nouveau"]
            self.cpp_info.components["libdrm_nouveau"].includedirs.extend([os.path.join("include", "libdrm"), os.path.join("include", "libdrm", "nouveau")])
            self.cpp_info.components["libdrm_nouveau"].requires = ["libdrm_libdrm"]
            self.cpp_info.components["libdrm_nouveau"].set_property("pkg_config_name", "libdrm_nouveau")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libdrm_nouveau"].system_libs = ["pthread"]

        if self.options.intel:
            self.cpp_info.components["libdrm_intel"].libs = ["drm_intel"]
            self.cpp_info.components["libdrm_intel"].includedirs.append(os.path.join("include", "libdrm"))
            self.cpp_info.components["libdrm_intel"].requires = ["libdrm_libdrm", "libpciaccess::libpciaccess"]
            self.cpp_info.components["libdrm_intel"].set_property("pkg_config_name", "libdrm_intel")

        if self.options.radeon:
            self.cpp_info.components["libdrm_radeon"].libs = ["drm_radeon"]
            self.cpp_info.components["libdrm_radeon"].includedirs.append(os.path.join("include", "libdrm"))
            self.cpp_info.components["libdrm_radeon"].requires = ["libdrm_libdrm"]
            self.cpp_info.components["libdrm_radeon"].set_property("pkg_config_name", "libdrm_radeon")
