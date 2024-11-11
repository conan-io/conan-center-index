from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.files import get, chdir, copy, export_conandata_patches, apply_conandata_patches, rename
from conan.tools.layout import basic_layout
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.microsoft import VCVars, is_msvc, NMakeDeps, NMakeToolchain
from conan.tools.apple import is_apple_os
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.55.0"


class MpdecimalConan(ConanFile):
    name = "mpdecimal"
    description = "mpdecimal is a package for correctly-rounded arbitrary precision decimal floating point arithmetic."
    license = "BSD-2-Clause"
    topics = ("multiprecision", "library")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.bytereef.org/mpdecimal"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
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
        self.folders.build = "src"

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
            self.tool_requires("automake/1.16.5")
        else:
            # required to support windows as a build machine
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
            tc_env = tc.environment()
            tc_env.append("LDXXFLAGS", ["$LDFLAGS"])
            tc.generate(tc_env)

    def _build_msvc(self):
        libmpdec_folder = self.source_path / "libmpdec"
        libmpdecpp_folder = self.source_path / "libmpdec++"

        mpdec_target = "libmpdec-{}.{}".format(self.version, "dll" if self.options.shared else "lib")
        mpdecpp_target = "libmpdec++-{}.{}".format(self.version, "dll" if self.options.shared else "lib")

        builds = [[libmpdec_folder, mpdec_target]]
        if self.options.cxx:
            builds.append([libmpdecpp_folder, mpdecpp_target])

        for build_dir, target in builds:
            copy(self, "Makefile.vc", build_dir, self.build_path)
            rename(self, self.build_path / "Makefile.vc", build_dir / "Makefile")

            with chdir(self, build_dir):
                self.run("""nmake -f Makefile.vc {target} MACHINE={machine} DEBUG={debug} DLL={dll}""".format(
                    target=target,
                    machine={"x86": "ppro", "x86_64": "x64"}[str(self.settings.arch)],
                    # FIXME: else, use ansi32 and ansi64
                    debug="1" if self.settings.build_type == "Debug" else "0",
                    dll="1" if self.options.shared else "0",
                ))

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
        versionsuffix = f".{self.version}" if self.options.shared else ""
        suffix = (
            f"{versionsuffix}{libsuffix}"
            if is_apple_os(self) or self.settings.os == "Windows"
            else f"{libsuffix}{versionsuffix}"
        )
        return f"libmpdec{suffix}", f"libmpdec++{suffix}"

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            self._build_msvc()
        else:
            autotools = Autotools(self)
            autotools.configure()
            libmpdec, libmpdecpp = self._target_names
            with chdir(self, "libmpdec"):
                autotools.make(target=libmpdec)
            if self.options.cxx:
                with chdir(self, "libmpdec++"):
                    autotools.make(target=libmpdecpp)

    def package(self):
        mpdecdir = os.path.join(self.source_folder, "libmpdec")
        mpdecppdir = os.path.join(self.source_folder, "libmpdec++")

        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "vccompat.h", src=mpdecdir, dst=os.path.join(self.package_folder, "include")) # 2.5.0/MSVC only
        copy(self, "mpdecimal.h", src=mpdecdir, dst=os.path.join(self.package_folder, "include"))
        if self.options.cxx:
            copy(self, "decimal.hh", src=mpdecppdir, dst=os.path.join(self.package_folder, "include"))
        builddirs = [mpdecdir]
        if self.options.cxx:
            builddirs.append(mpdecppdir)
        for builddir in builddirs:
            copy(self, "*.a",     src=builddir, dst=os.path.join(self.package_folder, "lib"))
            copy(self, "*.so",    src=builddir, dst=os.path.join(self.package_folder, "lib"))
            copy(self, "*.so.*",  src=builddir, dst=os.path.join(self.package_folder, "lib"))
            copy(self, "*.dylib", src=builddir, dst=os.path.join(self.package_folder, "lib"))
            copy(self, "*.lib",   src=builddir, dst=os.path.join(self.package_folder, "lib"))
            copy(self, "*.dll",   src=builddir, dst=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        lib_pre_suf = ("", "")
        if is_msvc(self):
            if self.options.shared:
                lib_pre_suf = ("lib", f"-{self.version}.dll")
            else:
                lib_pre_suf = ("lib", f"-{self.version}")
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
