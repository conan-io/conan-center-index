import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, replace_in_file, rm, collect_libs
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.53.0"


class GfCompleteConan(ConanFile):
    name = "gf-complete"
    description = "A library for Galois Field arithmetic"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ceph/gf-complete"
    topics = ("galois field", "math", "algorithms")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "neon": [True, False, "auto"],
        "sse": [True, False, "auto"],
        "avx": [True, False, "auto"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "neon": "auto",
        "sse": "auto",
        "avx": "auto",
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            self.options.rm_safe("sse")
            self.options.rm_safe("avx")
        if "arm" not in self.settings.arch:
            self.options.rm_safe("neon")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if is_msvc(self):
            self.requires("getopt-for-visual-studio/20200201")

    def validate(self):
        if is_msvc(self):
            if self.version == "1.03":
                raise ConanInvalidConfiguration("gf-complete 1.03 doesn't support Visual Studio")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Don't build tests and examples (and also tools if Visual Studio)
        to_build = ["src"]
        if not is_msvc(self):
            to_build.append("tools")
        replace_in_file(
            self,
            os.path.join(self.source_folder, "Makefile.am"),
            "SUBDIRS = src tools test examples",
            "SUBDIRS = {}".format(" ".join(to_build)),
        )
        # Honor build type settings and fPIC option
        for subdir in ["src", "tools"]:
            for flag in ["-O3", "-fPIC"]:
                replace_in_file(self, os.path.join(self.source_folder, subdir, "Makefile.am"), flag, "")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        if not is_msvc(self) and "x86" in self.settings.arch:
            tc.extra_cxxflags.append("-mstackrealign")
        yes_no = lambda v: "yes" if v else "no"
        if "arm" in str(self.settings.arch):
            if self.options.neon != "auto":
                tc.configure_args.append("--enable-neon={}".format(yes_no(self.options.neon)))
        if self.settings.arch in ["x86", "x86_64"]:
            if self.options.sse != "auto":
                tc.configure_args.append("--enable-sse={}".format(yes_no(self.options.sse)))
            if self.options.avx != "auto":
                tc.configure_args.append("--enable-avx={}".format(yes_no(self.options.avx)))
        if is_msvc(self):
            if self.options.shared:
                tc.extra_ldflags.append("-no-undefined")
                tc.extra_ldflags.append("-Wl,--export-all-symbols")
            tc.extra_cflags.append("-FS")
            tc.extra_cxxflags.append("-FS")
        tc.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f'{ar_wrapper} "lib -nologo"')
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

        if is_msvc(self):
            # Custom AutotoolsDeps for cl like compilers
            # workaround for https://github.com/conan-io/conan/issues/12784
            includedirs = []
            defines = []
            libs = []
            libdirs = []
            linkflags = []
            cxxflags = []
            cflags = []
            for dependency in reversed(self.dependencies.host.topological_sort.values()):
                deps_cpp_info = dependency.cpp_info.aggregated_components()
                includedirs.extend(deps_cpp_info.includedirs)
                defines.extend(deps_cpp_info.defines)
                libs.extend(deps_cpp_info.libs + deps_cpp_info.system_libs)
                libdirs.extend(deps_cpp_info.libdirs)
                linkflags.extend(deps_cpp_info.sharedlinkflags + deps_cpp_info.exelinkflags)
                cxxflags.extend(deps_cpp_info.cxxflags)
                cflags.extend(deps_cpp_info.cflags)
            env = Environment()
            env.append("CPPFLAGS", [f"-I{unix_path(self, p)}" for p in includedirs] + [f"-D{d}" for d in defines])
            env.append("_LINK_", [lib if lib.endswith(".lib") else f"{lib}.lib" for lib in libs])
            env.append("LDFLAGS", [f"-L{unix_path(self, p)}" for p in libdirs] + linkflags)
            env.append("CXXFLAGS", cxxflags)
            env.append("CFLAGS", cflags)
            env.vars(self).save_script("conanautotoolsdeps_cl_workaround")
        else:
            deps = AutotoolsDeps(self)
            deps.generate()

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rm(self, "*.la", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        if not is_msvc(self):
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.PATH.append(bin_path)
