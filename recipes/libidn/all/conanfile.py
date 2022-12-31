from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"

class LibIdnConan(ConanFile):
    name = "libidn"
    description = "GNU Libidn is a fully documented implementation of the Stringprep, Punycode and IDNA 2003 specifications."
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/libidn/"
    topics = ("encode", "decode", "internationalized", "domain", "name")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threads": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threads": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Shared libraries are not supported on Windows due to libtool limitation")

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

        tc = AutotoolsToolchain(self)
        if not self.options.shared:
            tc.extra_defines.append("LIBIDN_STATIC")
        if is_msvc(self):
            if Version(self.settings.compiler.version) >= "12":
                tc.extra_cflags.append("-FS")
            tc.extra_ldflags.extend("-L{}".format(p.replace("\\", "/")) for p in self.deps_cpp_info.lib_paths)

        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-threads={}".format(yes_no(self.options.threads)),
            "--with-libiconv-prefix={}".format(unix_path(self, self.deps_cpp_info["libiconv"].rootpath)),
            "--disable-nls",
            "--disable-rpath",
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
            env.vars(self).save_script("conanbuild_gsl_msvc")

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            if self.settings.arch in ("x86_64", "armv8", "armv8.3"):
                ssize = "signed long long int"
            else:
                ssize = "signed long int"
            replace_in_file(self,
                os.path.join(self.source_folder, "lib", "stringprep.h"),
                "ssize_t", ssize)
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["idn"]
        self.cpp_info.names["pkg_config"] = "libidn"
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.threads:
                self.cpp_info.system_libs = ["pthread"]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines = ["LIBIDN_STATIC"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)

