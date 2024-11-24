from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.files import get, chdir, copy, export_conandata_patches, apply_conandata_patches, rename, replace_in_file
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeToolchain
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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "2.5.0":
            del self.options.cxx

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.get_safe("cxx"):
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")
        self.folders.build = "src"

    def validate(self):
        if is_msvc(self) and self.settings.arch not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration(
                f"{self.ref} currently does not supported {self.settings.arch}. Contributions are welcomed")
        if self.options.get_safe("cxx") and Version(self.version) < "2.5.1":
            if self.options.shared and self.settings.os == "Windows":
                raise ConanInvalidConfiguration(
                    "A shared libmpdec++ is not possible on Windows (due to non-exportable thread local storage)")

    def build_requirements(self):
        if not is_msvc(self) and self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            if Version(self.version) >= "2.5.1" and self.options.shared:
                tc.extra_defines.append("MPDECIMAL_DLL")
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            if Version(self.version) >= "2.5.0":
                tc.configure_args.append("--enable-cxx" if self.options.cxx else "--disable-cxx")
            tc_env = tc.environment()
            tc_env.append("LDXXFLAGS", ["$LDFLAGS"])
            tc.generate(tc_env)

    @property
    def _target(self):
        return "SHARED" if self.options.shared else "STATIC"

    def _build_msvc(self):
        libmpdec_folder = os.path.join(self.source_folder, "libmpdec")
        libmpdecpp_folder = os.path.join(self.source_folder, "libmpdec++")

        builds = [libmpdec_folder]
        if self.options.get_safe("cxx"):
            builds.append(libmpdecpp_folder)

        for build_dir in builds:
            copy(self, "Makefile.vc", build_dir, self.build_folder)
            rename(self, os.path.join(self.build_folder, "Makefile.vc"), os.path.join(build_dir, "Makefile"))

            with chdir(self, build_dir):
                self.run("nmake -f Makefile.vc MACHINE={machine} DEBUG={debug} DLL={dll}".format(
                    machine={"x86": "ppro", "x86_64": "x64"}[str(self.settings.arch)],
                    # FIXME: else, use ansi32 and ansi64
                    debug="1" if self.settings.build_type == "Debug" else "0",
                    dll="1" if self.options.shared else "0",
                ))

    def build(self):
        apply_conandata_patches(self)
        # Replace the default target with just the target we want
        for ext in ["vc", "in"]:
            replace_in_file(self, os.path.join("libmpdec", f"Makefile.{ext}"), "default:",
                                f"default: $(LIB{self._target}) #")
            if self.options.get_safe("cxx"):
                replace_in_file(self, os.path.join("libmpdec++", f"Makefile.{ext}"), "default:",
                                    f"default: $(LIB{self._target}_CXX) #")
 
        if is_msvc(self):
            self._build_msvc()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        mpdecdir = os.path.join(self.source_folder, "libmpdec")
        mpdecppdir = os.path.join(self.source_folder, "libmpdec++")

        license_file = "LICENSE.txt" if Version(self.version) < "4.0.0" else "COPYRIGHT.txt"
        copy(self, license_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "vc*.h", src=mpdecdir, dst=os.path.join(self.package_folder, "include")) # <=2.5.0/MSVC only
        copy(self, "mpdecimal.h", src=mpdecdir, dst=os.path.join(self.package_folder, "include"))
        if self.options.get_safe("cxx"):
            copy(self, "decimal.hh", src=mpdecppdir, dst=os.path.join(self.package_folder, "include"))
        builddirs = [mpdecdir]
        if self.options.get_safe("cxx"):
            builddirs.append(mpdecppdir)
        for builddir in builddirs:
            for pattern in ["*.a", "*.so", "*.so.*", "*.dylib", "*.lib"]:
                copy(self, pattern, src=builddir, dst=os.path.join(self.package_folder, "lib"))
            copy(self, "*.dll", src=builddir, dst=os.path.join(self.package_folder, "bin"))

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
            define = "MPDECIMAL_DLL" if Version(self.version) >= "2.5.1" else "USE_DLL"
            self.cpp_info.components["libmpdecimal"].defines = [define]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libmpdecimal"].system_libs = ["m"]

        if self.options.get_safe("cxx"):
            self.cpp_info.components["libmpdecimal++"].libs = ["{}mpdec++{}".format(*lib_pre_suf)]
            self.cpp_info.components["libmpdecimal++"].requires = ["libmpdecimal"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libmpdecimal++"].system_libs = ["pthread"]
