from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.4"


class RubberbandConan(ConanFile):
    name = "rubberband"
    description = (
        "Library for changing the tempo and pitch of audio independently, "
        "with optional command-line tool and plugin interfaces."
    )
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://breakfastquay.com/rubberband/"
    topics = ("audio", "dsp", "time-stretch", "pitch-shift")
    package_type = "library"
    languages = ("C", "C++")
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

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        for opt in ("jni", "ladspa", "lv2", "vamp", "cmdline", "tests"):
            tc.project_options[opt] = "disabled"
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # MSVC + static: Meson also installs `librubberband.a` (Meson default) alongside `rubberband-static.lib`
        if is_msvc(self) and not self.options.shared:
            rm(self, "librubberband.a", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        if is_msvc(self) and not self.options.shared:
            self.cpp_info.libs = ["rubberband-static"]
            self.cpp_info.defines.append("RUBBERBAND_STATIC")
        else:
            self.cpp_info.libs = ["rubberband"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.append("pthread")
        if is_apple_os(self):
            # Default Meson fft=auto selects vDSP on Apple, which uses Accelerate.
            self.cpp_info.frameworks.append("Accelerate")
