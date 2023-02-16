from conan import ConanFile
from conan.tools.files import chdir, copy, get, rm, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, check_min_vs, unix_path
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.56.0"

class IslConan(ConanFile):
    name = "isl"
    description = "isl is a library for manipulating sets and relations of integer points bounded by linear constraints."
    topics = ("isl", "integer", "set", "library")
    license = "MIT"
    homepage = "https://libisl.sourceforge.io"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_int": ["gmp", "imath", "imath-32"],
        "autogen": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_int": "gmp",
        "autogen": False,
    }

    def package_id(self):
        self.info.options.rm_safe("autogen")

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

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Cannot build shared isl library on Windows (due to libtool refusing to link to static/import libraries)")
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("Apple M1 is not yet supported. Contributions are welcome")
        if self.options.with_int != "gmp":
            # FIXME: missing imath recipe
            raise ConanInvalidConfiguration("imath is not (yet) available on cci")
        if msvc_runtime_flag(self) == "MDd":
            # isl fails to link with this version of visual studio and MDd runtime: gmp.lib(bdiv_dbm1c.obj) : fatal error LNK1318: Unexpected PDB error; OK (0)
            check_min_vs(self, "192")

    def requirements(self):
        if self.options.with_int == "gmp":
            self.requires("gmp/6.2.1")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if self.options.autogen:
            self.tool_requires("autoconf/2.71")    # Needed for autoreconf
            self.tool_requires("automake/1.16.5")  # Needed for aclocal called by autoreconf--does Coanan 2.0 need a transitive_run trait?
            self.tool_requires("libtool/2.4.7")    # Needed for libtool

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self.source_folder)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append(f'--with-int={self.options.with_int}')
        tc.configure_args.append("--enable-portable-binary")
        if self.options.with_int == "gmp":
            tc.configure_args.append("--with-gmp=system")
            tc.configure_args.append(f'--with-gmp-prefix={unix_path(self, self.dependencies["gmp"].package_folder)}')
        if is_msvc(self):
            compiler_version = self.settings.get_safe("compiler.version")
            if compiler_version >= "191":
                tc.extra_cflags = ["-Zf"]
            if compiler_version >= "180":
                tc.extra_cflags = ["-FS"]
        # Visual Studio support for Conan 1.x; Can be remvoed when 2.0 is default
        if self.settings.get_safe("compiler") == "Visual Studio":
            compiler_version = self.settings.get_safe("compiler.version")
            if compiler_version >= "15":
                tc.extra_cflags = ["-Zf"]
            if compiler_version >= "12":
                tc.extra_cflags = ["-FS"]
        env = tc.environment()
        if is_msvc(self):
            env.define("CC", "cl -nologo")
            env.define("CXX", "cl -nologo")
        tc.generate(env)

    def build(self):
        if self.options.autogen:
            apply_conandata_patches(self) # Currently, the only patch is for the autogen use case
            with chdir(self, self.source_folder):
                command = "./autogen.sh"
                if os.path.exists(command):
                    self.run(command)
        autotools = Autotools(self)
        if is_msvc(self) and self.version == "0.24" and msvc_runtime_flag(self).startswith("MD"):
            # Pass BUILD flags to avoid confusion with GCC and mixing of runtime variants
            autotools.configure(args=['CC_FOR_BUILD=cl -nologo', f'CFLAGS_FOR_BUILD=-{msvc_runtime_flag(self)}'])
        else:
            autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", os.path.join(os.path.join(self.package_folder, "lib")))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "isl")
        self.cpp_info.libs = ["isl"]
