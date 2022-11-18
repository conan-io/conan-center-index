from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import copy, get, rename, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.53.0"


class CppunitConan(ConanFile):
    name = "cppunit"
    description = (
        "CppUnit is the C++ port of the famous JUnit framework for unit testing. "
        "Test output is in XML for automatic testing and GUI based for supervised tests."
    )
    topics = ("unit-test", "tdd")
    license = " LGPL-2.1-or-later"
    homepage = "https://freedesktop.org/wiki/Software/cppunit/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        if self.settings.os == "Windows" and self.options.shared:
            tc.extra_defines.append("CPPUNIT_BUILD_DLL")
        if is_msvc(self):
            tc.extra_cxxflags.append("-EHsc")
            if (self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) >= "12") or \
               (self.settings.compiler == "msvc" and Version(self.settings.compiler.version) >= "180"):
                tc.extra_cflags.append("-FS")
                tc.extra_cxxflags.append("-FS")
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            "--enable-debug={}".format(yes_no(self.settings.build_type == "Debug")),
            "--enable-doxygen=no",
            "--enable-dot=no",
            "--enable-werror=no",
            "--enable-html-docs=no",
        ])
        tc.generate()

        if is_msvc(self):
            env = Environment()
            compile_wrapper = unix_path(self, self._user_info_build["automake"].compile)
            ar_wrapper = unix_path(self, self._user_info_build["automake"].ar_lib)
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_cppunit_msvc")

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
        if is_msvc(self) and self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "cppunit.dll.lib"),
                         os.path.join(self.package_folder, "lib", "cppunit.lib"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "cppunit")
        self.cpp_info.libs = ["cppunit"]
        if not self.options.shared:
            libcxx = tools_legacy.stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("dl")
        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("CPPUNIT_DLL")
