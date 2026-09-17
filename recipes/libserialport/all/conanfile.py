from conan import ConanFile
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os

required_conan_version = ">=2"


class LibSerialPortConan(ConanFile):
    name = "libserialport"
    package_type = "library"
    description = "Minimal cross-platform serial port library in C"
    topics = ("serial", "rs232", "usb", "sigrok")
    license = "LGPL-3.0-or-later"
    homepage = "https://sigrok.org/wiki/libserialport"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "libusb": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "libusb": True,
        "shared": False,
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        basic_layout(self, src_folder='src')

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
            if is_msvc(self):
                self.tool_requires("automake/1.16.5")
        self.tool_requires("libtool/2.4.7")

    def requirements(self):
        if self.options.get_safe("libusb", False):
            self.requires("libusb/1.0.26")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        with_pic = self.options.shared or self.options.get_safe("fPIC", False)
        tc.configure_args.extend([
            "--with-pic={}".format(yes_no(with_pic)),
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--enable-static" if not self.options.shared else "--disable-static",
        ])
        env = tc.environment()
        if is_msvc(self):
            compile_wrapper = unix_path(self, self.conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, self.conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
        tc.generate(env)

        ad = AutotoolsDeps(self)
        ad.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["serialport"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["setupapi"])
        if is_apple_os(self):
            self.cpp_info.frameworks = ['IOKit', 'Foundation', 'CoreFoundation']
