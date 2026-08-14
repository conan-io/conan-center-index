from conan import ConanFile
from conan.tools.build import stdcpp_library
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, rm, rename
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.scm import Version
from conan.tools.meson import Meson, MesonToolchain

import os


required_conan_version = ">=2.0.9"

class OpenH264Conan(ConanFile):
    name = "openh264"
    description = "Open Source H.264 Codec"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.openh264.org/"
    topics = ("h264", "codec", "video", "compression", )
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    @property
    def _is_clang_cl(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'clang'

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.4.1 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.settings.arch in ["x86", "x86_64"]:
            self.tool_requires("nasm/2.16.01")
        if is_msvc(self) and self.settings.arch == "armv8":
            self.tool_requires("strawberryperl/[*]")
            self.tool_requires("gas-preprocessor/[*]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = MesonToolchain(self)
        tc.project_options["tests"] = "disabled"
        # clang-cl + Meson: MesonToolchain maps cppstd=23 to 'c++23', but Meson validates it via get_supported_arguments()
        # using -std=c++23 (GCC-style) instead of /std:c++23 (MSVC-style).
        # The test fails -> Meson rejects the value.
        # Using 'c++latest' works because Meson translates it to /std:c++latest which clang-cl accepts.
        # This is a Meson bug, not a clang-cl limitation - the workaround is safe even if a future clang-cl adds /std:c++23 support.
        if self._is_clang_cl and tc.cpp_std and "23" in tc.cpp_std:
            tc.cpp_std = "c++latest"
        # Clang 21+ warns on memcpy with non-trivially-copyable types (-Wnontrivial-memcall).
        # openh264 2.5.0 upstream uses memcpy on SWelsSvcCodingParam (with "confirmed_safe_unsafe_usage" comments),
        # and compiles with -Werror -> build fails.
        # Fixed in 2.6.0.
        if Version(self.version) < "2.6.0" and self.settings.compiler in ("clang", "apple-clang"):
            tc.extra_cxxflags.append("-Wno-nontrivial-memcall")
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        if is_msvc(self) or self._is_clang_cl:
            rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
            if not self.options.shared:
                rename(self, os.path.join(self.package_folder, "lib", "libopenh264.a"),
                        os.path.join(self.package_folder, "lib", "openh264.lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = [f"openh264"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.extend(["m", "pthread"])
        if self.settings.os == "Android":
            self.cpp_info.system_libs.append("m")
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                if self.settings.os == "Android" and libcxx == "c++_static":
                    # INFO: When builing for Android, need to link against c++abi too. Otherwise will get linkage errors:
                    # ld.lld: error: undefined symbol: operator new(unsigned long)
                    # >>> referenced by welsEncoderExt.cpp
                    self.cpp_info.system_libs.append("c++abi")
                self.cpp_info.system_libs.append(libcxx)
