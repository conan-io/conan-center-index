import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.53.0"


class LibIdn(ConanFile):
    name = "libidn2"
    description = (
        "GNU Libidn is a fully documented implementation of the Stringprep, Punycode and IDNA 2003"
        " specifications."
    )
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/libidn/"
    topics = ("libidn", "encode", "decode", "internationalized", "domain", "name")

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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")

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
        if not self.options.shared:
            tc.extra_defines.append("IDN2_STATIC")
        if is_msvc(self):
            tc.extra_cflags.append("-FS")
            tc.extra_cxxflags.append("-FS")
        tc.configure_args += [
            f"--with-libiconv-prefix={unix_path(self, self.dependencies['libiconv'].package_folder)}",
            "--disable-nls",
            "--disable-rpath",
        ]
        tc.generate()

        if is_msvc(self):
            env = Environment()
            dep_info = self.dependencies["libiconv"].cpp_info.aggregated_components()
            env.append("CPPFLAGS", [f"-I{unix_path(self, p)}" for p in dep_info.includedirs] + [f"-D{d}" for d in dep_info.defines])
            env.append("_LINK_", [lib if lib.endswith(".lib") else f"{lib}.lib" for lib in (dep_info.libs + dep_info.system_libs)])
            env.append("LDFLAGS", [f"-L{unix_path(self, p)}" for p in dep_info.libdirs] + dep_info.sharedlinkflags + dep_info.exelinkflags)
            env.append("CFLAGS", dep_info.cflags)
            env.vars(self).save_script("conanautotoolsdeps_cl_workaround")
        else:
            deps = AutotoolsDeps(self)
            deps.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            dumpbin_nm = unix_path(self, os.path.join(self.source_folder, "dumpbin_nm.py"))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f'{ar_wrapper} lib')
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libidn2.la"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

        if is_msvc(self) and self.options.shared:
            os.rename(os.path.join(self.package_folder, "lib", "idn2.dll.lib"),
                      os.path.join(self.package_folder, "lib", "idn2-0.lib"))
            copy(self, "idn2.exe",
                 os.path.join(self.build_folder, "src", ".libs"),
                 os.path.join(self.package_folder, "bin"))

    def package_info(self):
        if is_msvc(self) and self.options.shared:
            self.cpp_info.libs = ["idn2-0"]
        else:
            self.cpp_info.libs = ["idn2"]
        self.cpp_info.set_property("pkg_config_name", "libidn2")
        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.defines = ["IDN2_STATIC"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
