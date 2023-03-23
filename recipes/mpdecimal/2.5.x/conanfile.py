from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, Autotools
from conan.tools.files import get, chdir, load, copy, export_conandata_patches, apply_conandata_patches, mkdir
from conan.tools.microsoft import VCVars
from conan.tools.apple import is_apple_os
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import shutil
import pathlib
import os

required_conan_version = ">=1.33.0"


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

    generators = "AutotoolsDeps", "AutotoolsToolchain"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "setings_build", self.settings)

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.cxx:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def build_requirements(self):
        if self._is_msvc:
            self.build_requires("automake/1.16.4")
            if self._settings_build.os == "Windows" and not os.environ.get("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def validate(self):
        if self._is_msvc and self.settings.arch not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration("Arch is unsupported")
        if self.options.cxx:
            if self.options.shared and self.settings.os == "Windows":
                raise ConanInvalidConfiguration("A shared libmpdec++ is not possible on Windows (due to non-exportable thread local storage)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)

    def _build_msvc(self):
        build_dir = pathlib.Path(self.build_folder)
        libmpdec_folder = build_dir / self._source_subfolder / "libmpdec"
        libmpdecpp_folder = build_dir / self._source_subfolder / "libmpdec++"
        vcbuild_folder = build_dir / self._source_subfolder / "vcbuild"
        arch_ext = "{}".format(32 if self.settings.arch == "x86" else 64)
        dist_folder = vcbuild_folder / "dist{}".format(arch_ext)
        mkdir(self, dist_folder)

        shutil.copy(libmpdec_folder / "Makefile.vc", libmpdec_folder / "Makefile")

        autotools = AutotoolsToolchain(self)
        mpdec_extra_flags = []
        mpdecxx_extra_flags = []
        if Version(self.version) >= "2.5.1":
            if self.options.shared:
                mpdec_extra_flags = ["-DMPDECIMAL_DLL"]
                mpdecxx_extra_flags = ["-DLIBMPDECXX_DLL"]

        mpdec_target = "libmpdec-{}.{}".format(self.version, "dll" if self.options.shared else "lib")
        mpdecpp_target = "libmpdec++-{}.{}".format(self.version, "dll" if self.options.shared else "lib")

        builds = [[libmpdec_folder, mpdec_target, mpdec_extra_flags] ]
        if self.options.cxx:
            builds.append([libmpdecpp_folder, mpdecpp_target, mpdecxx_extra_flags])
        vcvars = VCVars(self)
        vcvars.generate()
        for build_dir, target, extra_flags in builds:
            with chdir(self, build_dir):
                self.run("""nmake /nologo /f Makefile.vc {target} MACHINE={machine} DEBUG={debug} DLL={dll} CONAN_CFLAGS="{cflags}" CONAN_CXXFLAGS="{cxxflags}" CONAN_LDFLAGS="{ldflags}" """.format(
                    target=target,
                    machine={"x86": "ppro", "x86_64": "x64"}[str(self.settings.arch)],  # FIXME: else, use ansi32 and ansi64
                    debug="1" if self.settings.build_type == "Debug" else "0",
                    dll="1" if self.options.shared else "0",
                    cflags=" ".join(autotools.cflags + extra_flags),
                    cxxflags=" ".join(autotools.cxxflags+ extra_flags),
                    ldflags=" ".join(autotools.ldflags),
                ))

        with chdir(self, libmpdec_folder):
            shutil.copy("mpdecimal.h", dist_folder)
            if self.options.shared:
                shutil.copy("libmpdec-{}.dll".format(self.version), dist_folder / "libmpdec-{}.dll".format(self.version))
                shutil.copy("libmpdec-{}.dll.exp".format(self.version), dist_folder / "libmpdec-{}.exp".format(self.version))
                shutil.copy("libmpdec-{}.dll.lib".format(self.version), dist_folder / "libmpdec-{}.lib".format(self.version))
            else:
                shutil.copy("libmpdec-{}.lib".format(self.version), dist_folder / "libmpdec-{}.lib".format(self.version))
        if self.options.cxx:
            with chdir(self, libmpdecpp_folder):
                shutil.copy("decimal.hh", dist_folder)
                shutil.copy("libmpdec++-{}.lib".format(self.version), dist_folder / "libmpdec++-{}.lib".format(self.version))

    def _configure_autotools(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--enable-cxx" if self.options.cxx else "--disable-cxx")
        tc.generate()

        deps = AutotoolsDeps(self)
        if is_apple_os(self) and self.settings.arch == "armv8":
            deps.environment.append("LDFLAGS", ["-arch arm64"])
            deps.environment.append("LDXXFLAGS", ["-arch arm64"])
        deps.generate()

        autotools = Autotools(self)
        autotools.configure(build_script_folder=self._source_subfolder)
        return autotools

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
        suffix = "{}{}".format(versionsuffix, libsuffix) if is_apple_os(self) or self.settings.os == "Windows" else "{}{}".format(libsuffix, versionsuffix)
        return "libmpdec{}".format(suffix), "libmpdec++{}".format(suffix)

    def build(self):
        self._patch_sources()
        if self._is_msvc:
            self._build_msvc()
        else:
            with chdir(self, self._source_subfolder):
                autotools = self._configure_autotools()
                self.output.info(load(self, pathlib.Path("libmpdec", "Makefile")))
                libmpdec, libmpdecpp = self._target_names
                with chdir(self, "libmpdec"):
                    autotools.make(target=libmpdec)
                if self.options.cxx:
                    with chdir(self, "libmpdec++"):
                        autotools.make(target=libmpdecpp)

    def package(self):
        pkg_dir = pathlib.Path(self.package_folder)
        copy(self, "LICENSE.txt", src=self._source_subfolder, dst=pkg_dir / "licenses")
        if self._is_msvc:
            build_dir = pathlib.Path(self.build_folder)
            distfolder = build_dir / self._source_subfolder / "vcbuild" / "dist{}".format(32 if self.settings.arch == "x86" else 64)
            copy(self, "vc*.h", src=build_dir / self._source_subfolder / "libmpdec", dst= pkg_dir/ "include")
            copy(self, "*.h", src=distfolder, dst= pkg_dir/ "include")
            if self.options.cxx:
                copy(self, "*.hh", src=distfolder, dst=pkg_dir / "include")
            self.copy(self, "*.lib", src=distfolder, dst=pkg_dir / "lib")
            self.copy(self, "*.dll", src=distfolder, dst=pkg_dir / "bin")
        else:
            src_dir = pathlib.Path(self._source_subfolder)
            mpdecdir = src_dir /  "libmpdec"
            mpdecppdir = src_dir / "libmpdec++"
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
        if self._is_msvc:
            lib_pre_suf = ("lib", "-{}".format(self.version))
        elif self.settings.os == "Windows":
            if self.options.shared:
                lib_pre_suf = ("", ".dll")

        self.cpp_info.components["libmpdecimal"].libs = ["{}mpdec{}".format(*lib_pre_suf)]
        if self.options.shared:
            if self._is_msvc:
                if Version(self.version) >= "2.5.1":
                    self.cpp_info.components["libmpdecimal"].defines = ["MPDECIMAL_DLL"]
                else:
                    self.cpp_info.components["libmpdecimal"].defines = ["USE_DLL"]
        else:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libmpdecimal"].system_libs = ["m"]

        if self.options.cxx:
            self.cpp_info.components["libmpdecimal++"].libs = ["{}mpdec++{}".format(*lib_pre_suf)]
            self.cpp_info.components["libmpdecimal++"].requires = ["libmpdecimal"]
            if self.options.shared:
                if Version(self.version) >= "2.5.1":
                    self.cpp_info.components["libmpdecimal"].defines = ["MPDECIMALXX_DLL"]
