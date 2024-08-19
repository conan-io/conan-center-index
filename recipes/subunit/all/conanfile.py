import glob
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class SubunitConan(ConanFile):
    name = "subunit"
    description = "A streaming protocol for test results"
    license = ("Apache-2.0", "BSD-3-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://launchpad.net/subunit"
    topics = ("subunit", "streaming", "protocol", "test", "results")

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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_clang_cl(self):
        return self.settings.os == "Windows" and self.settings.compiler == "clang"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cppunit/1.15.1", transitive_headers=True)

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Cannot build shared subunit libraries on Windows")
        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "10":
            # Complete error is:
            # make[2]: *** No rule to make target `/Applications/Xcode-9.4.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.13.sdk/System/Library/Perl/5.18/darwin-thread-multi-2level/CORE/config.h', needed by `Makefile'.  Stop.
            raise ConanInvalidConfiguration("Due to weird make error involving missing config.h file in sysroot")
        if self.settings.compiler == "apple-clang" and self.options.shared:
            raise ConanInvalidConfiguration("Shared builds with apple-clang are not supported")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        if is_msvc(self):
            tc.extra_cflags.append("-FS")
            tc.extra_cxxflags.append("-FS")
            tc.extra_cxxflags.append("-EHsc")
        tc.configure_args.append("CHECK_CFLAGS= ")
        tc.configure_args.append("CHECK_LIBS= ")
        cppunit_info = self.dependencies["cppunit"].cpp_info
        tc.configure_args.append("CPPUNIT_LIBS='{}'".format(" ".join(cppunit_info.libs)))
        tc.configure_args.append("CPPUNIT_CFLAGS= ")
        # Avoid installing i18n + perl things in arch-dependent folders or in a `local` subfolder
        tc.make_args += [
            f"INSTALLARCHLIB={unix_path(self, os.path.join(self.package_folder, 'lib'))}",
            f"INSTALLSITEARCH={unix_path(self, os.path.join(self.build_folder, 'archlib'))}",
            f"INSTALLVENDORARCH={unix_path(self, os.path.join(self.build_folder, 'archlib'))}",
            f"INSTALLSITEBIN={unix_path(self, os.path.join(self.package_folder, 'bin'))}",
            f"INSTALLSITESCRIPT={unix_path(self, os.path.join(self.package_folder, 'bin'))}",
            f"INSTALLSITEMAN1DIR={unix_path(self, os.path.join(self.build_folder, 'share', 'man', 'man1'))}",
            f"INSTALLSITEMAN3DIR={unix_path(self, os.path.join(self.build_folder, 'share', 'man', 'man3'))}",
        ]
        tc.generate()

        if is_msvc(self) or self._is_clang_cl:
            # AutotoolsDeps causes ./configure to fail on Windows
            # Possibly related to https://github.com/conan-io/conan/issues/12784
            env = Environment()
            env.append("CPPFLAGS", [f"-I{unix_path(self, p)}" for p in cppunit_info.includedirs] + [f"-D{d}" for d in cppunit_info.defines])
            env.vars(self).save_script("conanautotoolsdeps_workaround")
        else:
            deps = AutotoolsDeps(self)
            deps.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f'{ar_wrapper} lib')
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rm(self, "*.la", self.package_folder, recursive=True)
        rm(self, "*.pod", self.package_folder, recursive=True)
        for d in glob.glob(os.path.join(self.package_folder, "lib", "python*")):
            rmdir(self, d)
        for d in glob.glob(os.path.join(self.package_folder, "lib", "*")):
            if os.path.isdir(d):
                rmdir(self, d)
        for d in glob.glob(os.path.join(self.package_folder, "*")):
            if os.path.isdir(d) and os.path.basename(d) not in ["bin", "include", "lib", "licenses"]:
                rmdir(self, d)

    def package_info(self):
        self.cpp_info.components["libsubunit"].libs = ["subunit"]
        self.cpp_info.components["libsubunit"].set_property("pkg_config_name", "libsubunit")
        self.cpp_info.components["libcppunit_subunit"].libs = ["cppunit_subunit"]
        self.cpp_info.components["libcppunit_subunit"].requires = ["cppunit::cppunit"]
        self.cpp_info.components["libcppunit_subunit"].set_property("pkg_config_name", "libcppunit_subunit")

        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
