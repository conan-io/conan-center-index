import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.0"


class Libv4lConan(ConanFile):
    name = "libv4l"
    description = "libv4l is a collection of libraries which adds a thin abstraction layer on top of video4linux2 devices."
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://linuxtv.org/wiki/index.php/V4l-utils"
    topics = ("video4linux2", "v4l", "video", "camera", "webcam")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_plugins": [True, False],
        "build_wrappers": [True, False],
        "build_libdvbv5": [True, False],
        "with_jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg", False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_plugins": True,
        "build_wrappers": True,
        "build_libdvbv5": False,
        "with_jpeg": "libjpeg",
    }

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.build_libdvbv5:
            self.requires("libudev/255.13")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.2")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("libv4l is only supported on Linux")
        check_min_cppstd(self, 11)

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("gettext/0.22.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        feature = lambda option: "enabled" if option else "disabled"
        true_false = lambda option: "true" if option else "false"
        tc = MesonToolchain(self)
        tc.project_options["bpf"] = "disabled"  # Requires Clang
        tc.project_options["gconv"] = "enabled"
        tc.project_options["jpeg"] = feature(self.options.with_jpeg)
        tc.project_options["libdvbv5"] = feature(self.options.build_libdvbv5)
        tc.project_options["v4l-plugins"] = true_false(self.options.build_plugins)
        tc.project_options["v4l-wrappers"] = true_false(self.options.build_wrappers)
        # Disable executables to simplify the recipe
        tc.project_options["v4l-utils"] = "false"
        tc.project_options["qv4l2"] = "disabled"
        tc.project_options["qvidcap"] = "disabled"
        tc.project_options["v4l2-tracer"] = "disabled"
        # Doxygen options
        tc.project_options["doxygen-doc"] = "disabled"
        tc.project_options["doxygen-html"] = "false"
        tc.project_options["doxygen-man"] = "false"
        # tc.project_options["gconvsysdir"] = ""
        # tc.project_options["libv4l1subdir"] = ""
        # tc.project_options["libv4l2subdir"] = ""
        # tc.project_options["libv4lconvertsubdir"] = ""
        # tc.project_options["systemdsystemunitdir"] = ""
        # tc.project_options["udevdir"] = ""
        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING.libv4l", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if self.options.build_libdvbv5:
            copy(self, "COPYING.libdvbv5", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.rename(os.path.join(self.package_folder, "share"),
                  os.path.join(self.package_folder, "res"))

    def package_info(self):
        libjpeg = []
        if self.options.with_jpeg == "libjpeg":
            libjpeg = ["libjpeg::libjpeg"]
        elif self.options.with_jpeg == "libjpeg-turbo":
            libjpeg = ["libjpeg-turbo::jpeg"]
        elif self.options.with_jpeg == "mozjpeg":
            libjpeg = ["mozjpeg::libjpeg"]

        # libv4lconvert: v4l format conversion library
        self.cpp_info.components["libv4lconvert"].libs = ["v4lconvert"]
        self.cpp_info.components["libv4lconvert"].requires = libjpeg
        self.cpp_info.components["libv4lconvert"].system_libs = ["m", "rt"]

        # libv4l2: v4l2 device access library
        self.cpp_info.components["libv4l2"].set_property("pkg_config_name", "libv4l2")
        self.cpp_info.components["libv4l2"].libs = ["v4l2"]
        self.cpp_info.components["libv4l2"].requires = ["libv4lconvert"]
        self.cpp_info.components["libv4l2"].system_libs = ["dl", "pthread"]

        # libv4l2rds: v4l2 RDS decode library
        self.cpp_info.components["libv4l2rds"].set_property("pkg_config_name", "libv4l2rds")
        self.cpp_info.components["libv4l2rds"].libs = ["v4l2rds"]
        self.cpp_info.components["libv4l2rds"].system_libs = ["pthread"]

        # libv4l1: v4l1 compatibility library
        self.cpp_info.components["libv4l1"].set_property("pkg_config_name", "libv4l1")
        self.cpp_info.components["libv4l1"].libs = ["v4l1"]
        self.cpp_info.components["libv4l1"].requires = ["libv4l2"]
        self.cpp_info.components["libv4l1"].system_libs = ["pthread"]

        if self.options.build_libdvbv5:
            # libdvbv5: DVBv5 utility library
            self.cpp_info.components["libdvbv5"].set_property("pkg_config_name", "libdvbv5")
            self.cpp_info.components["libdvbv5"].libs = ["dvbv5"]
            self.cpp_info.components["libdvbv5"].requires = ["libudev::libudev"]
            self.cpp_info.components["libdvbv5"].system_libs = ["m", "rt", "pthread"]
            self.cpp_info.components["libdvbv5"].resdirs = ["res"]
