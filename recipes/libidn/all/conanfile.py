import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import get, rmdir, export_conandata_patches, apply_conandata_patches, copy, chdir, replace_in_file, rm
from conan.tools.gnu import AutotoolsToolchain, Autotools, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path, is_msvc, check_min_vs

required_conan_version = ">=1.33.0"


class LibIdnConan(ConanFile):
    name = "libidn"
    description = "GNU Libidn is a fully documented implementation of the Stringprep, Punycode and IDNA 2003 specifications."
    homepage = "https://www.gnu.org/software/libidn/"
    topics = ("libidn", "encode", "decode", "internationalized", "domain", "name")
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
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

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Shared libraries are not supported on Windows due to libtool limitation")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("cccl/1.3")

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
            tc.defines.append("LIBIDN_STATIC")
        env = tc.environment()
        if is_msvc(self):
            env.define("CC", "cccl")
            env.define("CXX", "cccl")
            env.define("LD", "cccl")
            if check_min_vs(self, 180, raise_invalid=False):
                tc.extra_cflags.append("-FS")
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args += [
            "--enable-threads={}".format(yes_no(self.options.threads)),
            "--with-libiconv-prefix={}".format(unix_path(self, self.dependencies["libiconv"].package_folder)),
            "--disable-csharp",
            "--disable-nls",
            "--disable-rpath",
        ]
        tc.generate(env)
        deps = AutotoolsDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            if self.settings.arch in ("x86_64", "armv8", "armv8.3"):
                ssize = "signed long long int"
            else:
                ssize = "signed long int"
            replace_in_file(self, os.path.join(self.source_folder, "lib", "stringprep.h"), "ssize_t", ssize)
        if self.settings.os == "Windows":
            # Otherwise tries to create a symlink from GNUmakefile to itself, which fails on Windows
            replace_in_file(self, os.path.join(self.source_folder, "configure"),
                            '"$GNUmakefile") CONFIG_LINKS="$CONFIG_LINKS $GNUmakefile:$GNUmakefile" ;;', "")
            replace_in_file(self, os.path.join(self.source_folder, "configure"),
                            'ac_config_links="$ac_config_links $GNUmakefile:$GNUmakefile"', "")

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make(args=["V=1"])

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["idn"]
        self.cpp_info.set_property("pkg_config_name", "libidn")
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.threads:
                self.cpp_info.system_libs = ["pthread"]
        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.defines = ["LIBIDN_STATIC"]

        # TODO: to remove in conan v2
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
