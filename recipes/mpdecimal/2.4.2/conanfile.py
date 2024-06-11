import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, replace_in_file, rmdir, mkdir, rename
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, VCVars, NMakeDeps, NMakeToolchain

required_conan_version = ">=1.53.0"


class MpdecimalConan(ConanFile):
    name = "mpdecimal"
    description = (
        "mpdecimal is a package for correctly-rounded arbitrary precision decimal floating point arithmetic."
    )
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.bytereef.org/mpdecimal"
    topics = ("multiprecision", "library")

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
        return getattr(self, "setings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self) and self.settings.arch not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration(
                f"{self.ref} currently does not supported {self.settings.arch}. Contributions are welcomed")

    def build_requirements(self):
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")
        else:
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
            tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            if not cross_building(self):
                env = VirtualRunEnv(self)
                env.generate(scope="build")

            tc = AutotoolsToolchain(self)
            tc.generate()

            deps = AutotoolsDeps(self)
            if is_apple_os(self) and self.settings.arch == "armv8":
                deps.environment.append("LDFLAGS", ["-arch arm64"])
                deps.environment.append("LDXXFLAGS", ["-arch arm64"])
            deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if not is_msvc(self):
            """
            Using autotools:
            - Build only shared libraries when shared == True
            - Build only static libraries when shared == False
            ! This is more complicated on Windows because when shared=True, an implicit static library has to be built
            """

            shared_ext_mapping = {
                "Linux": ".so",
                "Windows": ".dll",
                "Macos": ".dylib",
            }
            shared_ext = shared_ext_mapping[str(self.settings.os)]
            static_ext = ".a"
            main_version, _ = self.version.split(".", 1)

            replace_in_file(self, os.path.join(self.source_folder, "configure"),
                            "libmpdec.a", f"libmpdec{static_ext}")
            replace_in_file(self, os.path.join(self.source_folder, "configure"),
                            "libmpdec.so", f"libmpdec{shared_ext}")

            makefile_in = os.path.join(self.source_folder, "Makefile.in")
            mpdec_makefile_in = os.path.join(self.source_folder, "libmpdec", "Makefile.in")
            replace_in_file(self, makefile_in, "libdir = @libdir@", "libdir = @libdir@\nbindir = @bindir@")
            if self.options.shared:
                if self.settings.os == "Windows":
                    replace_in_file(self, makefile_in,
                                    "LIBSHARED = @LIBSHARED@",
                                    f"LIBSHARED = libmpdec-{main_version}{shared_ext}")
                    replace_in_file(self, makefile_in,
                                    "install: FORCE",
                                    "install: FORCE\n\t$(INSTALL) -d -m 755 $(DESTDIR)$(bindir)")
                    replace_in_file(self, makefile_in,
                                    "\t$(INSTALL) -m 755 libmpdec/$(LIBSHARED) $(DESTDIR)$(libdir)\n",
                                    "\t$(INSTALL) -m 755 libmpdec/$(LIBSHARED) $(DESTDIR)$(bindir)\n")
                    replace_in_file(self, makefile_in,
                                    "\tcd $(DESTDIR)$(libdir) && ln -sf $(LIBSHARED) $(LIBSONAME) && ln -sf $(LIBSHARED) libmpdec.so\n",
                                    "")
                else:
                    replace_in_file(self, makefile_in,
                                    "\t$(INSTALL) -m 644 libmpdec/$(LIBSTATIC) $(DESTDIR)$(libdir)\n",
                                    "")
                    replace_in_file(self, makefile_in,
                                    "\tcd $(DESTDIR)$(libdir) && ln -sf $(LIBSHARED) $(LIBSONAME) && ln -sf $(LIBSHARED) libmpdec.so",
                                    f"\tcd $(DESTDIR)$(libdir) && ln -sf $(LIBSHARED) $(LIBSONAME) && ln -sf $(LIBSHARED) libmpdec{shared_ext}")
            else:
                replace_in_file(self, makefile_in,
                                "\t$(INSTALL) -m 755 libmpdec/$(LIBSHARED) $(DESTDIR)$(libdir)\n",
                                "")
                replace_in_file(self, makefile_in,
                                "\tcd $(DESTDIR)$(libdir) && ln -sf $(LIBSHARED) $(LIBSONAME) && ln -sf $(LIBSHARED) libmpdec.so\n",
                                "")

            replace_in_file(self, mpdec_makefile_in,
                            "default: $(LIBSTATIC) $(LIBSHARED)",
                            "default: $({})".format("LIBSHARED" if self.options.shared else "LIBSTATIC"))

            if self.settings.os == "Windows":
                replace_in_file(self, mpdec_makefile_in,
                                "LIBSHARED = @LIBSHARED@",
                                f"LIBSHARED = libmpdec-{main_version}{shared_ext}")
                replace_in_file(self, mpdec_makefile_in, "\tln -sf $(LIBSHARED) libmpdec.so", "")
                replace_in_file(self, mpdec_makefile_in, "\tln -sf $(LIBSHARED) $(LIBSONAME)", "")
                replace_in_file(self, mpdec_makefile_in,
                                "CONFIGURE_LDFLAGS =",
                                f"CONFIGURE_LDFLAGS = -Wl,--out-implib,libmpdec{static_ext}")
            else:
                replace_in_file(self, mpdec_makefile_in, "libmpdec.so", f"libmpdec{shared_ext}")

    @property
    def _libmpdec_folder(self):
        return self.source_path / "libmpdec"

    @property
    def _dist_folder(self):
        vcbuild_folder = self.build_path / "vcbuild"
        arch_ext = "32" if self.settings.arch == "x86" else "64"
        return vcbuild_folder / f"dist{arch_ext}"

    def _build_msvc(self):
        libmpdec_folder = self._libmpdec_folder
        copy(self, "Makefile.vc", libmpdec_folder, self.build_path)
        rename(self, self.build_path / "Makefile.vc", libmpdec_folder / "Makefile")

        ext = "dll" if self.options.shared else "lib"
        mpdec_target = f"libmpdec-{self.version}.{ext}"

        with chdir(self, libmpdec_folder):
            self.run("nmake -f Makefile.vc {target} MACHINE={machine} DEBUG={debug} DLL={dll}".format(
                target=mpdec_target,
                machine={"x86": "ppro", "x86_64": "x64"}[str(self.settings.arch)],
                # FIXME: else, use ansi32 and ansi64
                debug="1" if self.settings.build_type == "Debug" else "0",
                dll="1" if self.options.shared else "0",
            ))

        dist_folder = self._dist_folder
        mkdir(self, dist_folder)
        copy(self, "mpdecimal.h", libmpdec_folder, dist_folder)
        if self.options.shared:
            copy(self, "*.dll", libmpdec_folder, dist_folder)
            copy(self, "*.dll.exp", libmpdec_folder, dist_folder)
            copy(self, "*.dll.lib", libmpdec_folder, dist_folder)
        else:
            copy(self, "*.lib", libmpdec_folder, dist_folder)

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            self._build_msvc()
        else:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.configure()
                autotools.make()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            dist_folder = self._dist_folder
            copy(self, "vc*.h", src=self._libmpdec_folder, dst=os.path.join(self.package_folder, "include"))
            copy(self, "*.h", src=dist_folder, dst=os.path.join(self.package_folder, "include"))
            copy(self, "*.lib", src=dist_folder, dst=os.path.join(self.package_folder, "lib"))
            copy(self, "*.dll", src=dist_folder, dst=os.path.join(self.package_folder, "bin"))
        else:
            with chdir(self, os.path.join(self.source_folder)):
                autotools = Autotools(self)
                autotools.install()
            rmdir(self, os.path.join(self.package_folder, "share"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        if is_msvc(self):
            if self.options.shared:
                self.cpp_info.libs = [f"libmpdec-{self.version}.dll"]
            else:
                self.cpp_info.libs = [f"libmpdec-{self.version}"]
        else:
            self.cpp_info.libs = ["mpdec"]
        if self.options.shared:
            if is_msvc(self):
                self.cpp_info.defines = ["USE_DLL"]
        else:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs = ["m"]
