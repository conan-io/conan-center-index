from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, Autotools
from conan.tools.files import get, chdir, copy, export_conandata_patches, apply_conandata_patches, mkdir, rename
from conan.tools.layout import basic_layout
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.microsoft import VCVars, is_msvc, NMakeDeps, NMakeToolchain
from conan.tools.apple import is_apple_os
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import pathlib

required_conan_version = ">=1.55.0"


class MpdecimalConan(ConanFile):
    name = "mpdecimal"
    description = "mpdecimal is a package for correctly-rounded arbitrary precision decimal floating point arithmetic."
    license = "BSD-2-Clause"
    topics = ("mpdecimal", "multiprecision", "library")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.bytereef.org/mpdecimal"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cxx": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cxx": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "setings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.cxx:
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self) and self.settings.arch not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration(
                f"{self.ref} currently does not supported {self.settings.arch}. Contributions are welcomed")
        if self.options.cxx:
            if self.options.shared and self.settings.os == "Windows":
                raise ConanInvalidConfiguration(
                    "A shared libmpdec++ is not possible on Windows (due to non-exportable thread local storage)")

    def build_requirements(self):
        if is_msvc(self):
            self.tool_requires("automake/1.16.4")
        else:
            # required to suppport windows as a build machine
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            vcvars = VCVars(self)
            vcvars.generate()

            deps = NMakeDeps(self)
            deps.generate()

            tc = NMakeToolchain(self)
            if Version(self.version) >= "2.5.1":
                if self.options.shared:
                    tc.extra_cflags.append("-DMPDECIMAL_DLL")
                    if self.options.cxx:
                        tc.extra_cxxflags.append("-DLIBMPDECXX_DLL")
            tc.generate()
        else:
            # inject tool_requires env vars in build scope (not needed if there is no tool_requires)
            env = VirtualBuildEnv(self)
            env.generate()
            # inject requires env vars in build scope
            # it's required in case of native build when there is AutotoolsDeps & at least one dependency which might be shared, because configure tries to run a test executable
            if not cross_building(self):
                env = VirtualRunEnv(self)
                env.generate(scope="build")

            tc = AutotoolsToolchain(self)
            tc.configure_args.append("--enable-cxx" if self.options.cxx else "--disable-cxx")
            tc.generate()

            deps = AutotoolsDeps(self)
            if is_apple_os(self) and self.settings.arch == "armv8":
                deps.environment.append("LDFLAGS", ["-arch arm64"])
                deps.environment.append("LDXXFLAGS", ["-arch arm64"])
            deps.generate()

    def _build_msvc(self):
        source_dir = pathlib.Path(self.source_folder)
        build_dir = pathlib.Path(self.build_folder)
        libmpdec_folder = source_dir / "libmpdec"
        libmpdecpp_folder = source_dir / "libmpdec++"
        vcbuild_folder = build_dir / "vcbuild"
        arch_ext = "{}".format(32 if self.settings.arch == "x86" else 64)
        dist_folder = vcbuild_folder / "dist{}".format(arch_ext)
        mkdir(self, dist_folder)

        copy(self, "Makefile.vc", libmpdec_folder, build_dir)
        rename(self, build_dir / "Makefile.vc", libmpdec_folder / "Makefile")

        mpdec_target = "libmpdec-{}.{}".format(self.version, "dll" if self.options.shared else "lib")
        mpdecpp_target = "libmpdec++-{}.{}".format(self.version, "dll" if self.options.shared else "lib")

        builds = [[libmpdec_folder, mpdec_target]]
        if self.options.cxx:
            builds.append([libmpdecpp_folder, mpdecpp_target])

        for build_dir, target in builds:
            with chdir(self, build_dir):
                self.run("""nmake -f Makefile.vc {target} MACHINE={machine} DEBUG={debug} DLL={dll}""".format(
                    target=target,
                    machine={"x86": "ppro", "x86_64": "x64"}[str(self.settings.arch)],
                    # FIXME: else, use ansi32 and ansi64
                    debug="1" if self.settings.build_type == "Debug" else "0",
                    dll="1" if self.options.shared else "0",
                ))

        copy(self, "mpdecimal.h", libmpdec_folder, dist_folder)
        if self.options.shared:
            copy(self, "libmpdec-{}.dll".format(self.version), libmpdec_folder, dist_folder)
            copy(self, "libmpdec-{}.dll.exp".format(self.version), libmpdec_folder, dist_folder)
            copy(self, "libmpdec-{}.dll.lib".format(self.version), libmpdec_folder, dist_folder)
        else:
            copy(self, "libmpdec-{}.lib".format(self.version), libmpdec_folder, dist_folder)
        if self.options.cxx:
            copy(self, "decimal.hh", libmpdecpp_folder, dist_folder)
            copy(self, "libmpdec++-{}.lib".format(self.version), libmpdecpp_folder, dist_folder)

    @property
    def _shared_suffix(self):
        if is_apple_os(self):
            return ".dylib"
        return {
            "Windows": ".dll",
        }.get(str(self.settings.os), ".so")

    @property
    def _target_names(self):
        libsuffix = self._shared_suffix if self.options.shared else ".a"
        versionsuffix = ".{}".format(self.version) if self.options.shared else ""
        suffix = "{}{}".format(versionsuffix, libsuffix) if is_apple_os(
            self) or self.settings.os == "Windows" else "{}{}".format(libsuffix, versionsuffix)
        return "libmpdec{}".format(suffix), "libmpdec++{}".format(suffix)

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            self._build_msvc()
        else:
            autotools = Autotools(self)
            autotools.configure()
            # self.output.info(load(self, pathlib.Path("libmpdec", "Makefile")))
            libmpdec, libmpdecpp = self._target_names
            copy(self, "*", pathlib.Path(self.source_folder, "libmpdec"), pathlib.Path(self.build_folder, "libmpdec"))
            with chdir(self, "libmpdec"):
                autotools.make(target=libmpdec)
            if self.options.cxx:
                copy(self, "*", pathlib.Path(self.source_folder, "libmpdec++"),
                     pathlib.Path(self.build_folder, "libmpdec++"))
                with chdir(self, "libmpdec++"):
                    autotools.make(target=libmpdecpp)

    def package(self):
        source_dir = pathlib.Path(self.source_folder)
        pkg_dir = pathlib.Path(self.package_folder)
        copy(self, "LICENSE.txt", src=self.source_folder, dst=pkg_dir / "licenses")
        if is_msvc(self):
            build_dir = pathlib.Path(self.build_folder)
            distfolder = build_dir / "vcbuild" / "dist{}".format(32 if self.settings.arch == "x86" else 64)
            copy(self, "vc*.h", src=source_dir / "libmpdec", dst=pkg_dir / "include")
            copy(self, "*.h", src=distfolder, dst=pkg_dir / "include")
            if self.options.cxx:
                copy(self, "*.hh", src=distfolder, dst=pkg_dir / "include")
            copy(self, "*.lib", src=distfolder, dst=pkg_dir / "lib")
            copy(self, "*.dll", src=distfolder, dst=pkg_dir / "bin")
        else:
            build_dir = pathlib.Path(self.build_folder)
            mpdecdir = build_dir / "libmpdec"
            mpdecppdir = build_dir / "libmpdec++"
            copy(self, "mpdecimal.h", src=mpdecdir, dst=pkg_dir / "include")
            if self.options.cxx:
                copy(self, "decimal.hh", src=mpdecppdir, dst=pkg_dir / "include")
            builddirs = [mpdecdir]
            if self.options.cxx:
                builddirs.append(mpdecppdir)
            for builddir in builddirs:
                copy(self, "*.a", src=builddir, dst=pkg_dir / "lib")
                copy(self, "*.so", src=builddir, dst=pkg_dir / "lib")
                copy(self, "*.so.*", src=builddir, dst=pkg_dir / "lib")
                copy(self, "*.dylib", src=builddir, dst=pkg_dir / "lib")
                copy(self, "*.dll", src=builddir, dst=pkg_dir / "bin")

    def package_info(self):
        lib_pre_suf = ("", "")
        if is_msvc(self):
            lib_pre_suf = ("lib", "-{}".format(self.version))
        elif self.settings.os == "Windows":
            if self.options.shared:
                lib_pre_suf = ("", ".dll")

        self.cpp_info.components["libmpdecimal"].libs = ["{}mpdec{}".format(*lib_pre_suf)]
        if self.options.shared and is_msvc(self):
            if Version(self.version) >= "2.5.1":
                self.cpp_info.components["libmpdecimal"].defines = ["MPDECIMAL_DLL"]
            else:
                self.cpp_info.components["libmpdecimal"].defines = ["USE_DLL"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libmpdecimal"].system_libs = ["m"]

        if self.options.cxx:
            self.cpp_info.components["libmpdecimal++"].libs = ["{}mpdec++{}".format(*lib_pre_suf)]
            self.cpp_info.components["libmpdecimal++"].requires = ["libmpdecimal"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libmpdecimal++"].system_libs = ["pthread"]
            if self.options.shared and Version(self.version) >= "2.5.1":
                self.cpp_info.components["libmpdecimal"].defines = ["MPDECIMALXX_DLL"]
