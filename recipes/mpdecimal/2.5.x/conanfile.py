from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os
import shutil

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

    _autotools = None

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
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

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
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def validate(self):
        if self._is_msvc and self.settings.arch not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration("Arch is unsupported")
        if self.options.cxx:
            if self.options.shared and self.settings.os == "Windows":
                raise ConanInvalidConfiguration("A shared libmpdec++ is not possible on Windows (due to non-exportable thread local storage)")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def _build_msvc(self):
        libmpdec_folder = os.path.join(self.build_folder, self._source_subfolder, "libmpdec")
        libmpdecpp_folder = os.path.join(self.build_folder, self._source_subfolder, "libmpdec++")
        vcbuild_folder = os.path.join(self.build_folder, self._source_subfolder, "vcbuild")
        arch_ext = "{}".format(32 if self.settings.arch == "x86" else 64)
        dist_folder = os.path.join(vcbuild_folder, "dist{}".format(arch_ext))
        os.mkdir(dist_folder)

        shutil.copy(os.path.join(libmpdec_folder, "Makefile.vc"), os.path.join(libmpdec_folder, "Makefile"))

        autotools = AutoToolsBuildEnvironment(self)
        mpdec_extra_flags = []
        mpdecxx_extra_flags = []
        if tools.scm.Version(self, self.version) >= "2.5.1":
            if self.options.shared:
                mpdec_extra_flags = ["-DMPDECIMAL_DLL"]
                mpdecxx_extra_flags = ["-DLIBMPDECXX_DLL"]

        mpdec_target = "libmpdec-{}.{}".format(self.version, "dll" if self.options.shared else "lib")
        mpdecpp_target = "libmpdec++-{}.{}".format(self.version, "dll" if self.options.shared else "lib")

        builds = [[libmpdec_folder, mpdec_target, mpdec_extra_flags] ]
        if self.options.cxx:
            builds.append([libmpdecpp_folder, mpdecpp_target, mpdecxx_extra_flags])
        with tools.vcvars(self):
            for build_dir, target, extra_flags in builds:
                with tools.files.chdir(self, build_dir):
                    self.run("""nmake /nologo /f Makefile.vc {target} MACHINE={machine} DEBUG={debug} DLL={dll} CONAN_CFLAGS="{cflags}" CONAN_CXXFLAGS="{cxxflags}" CONAN_LDFLAGS="{ldflags}" """.format(
                        target=target,
                        machine={"x86": "ppro", "x86_64": "x64"}[str(self.settings.arch)],  # FIXME: else, use ansi32 and ansi64
                        debug="1" if self.settings.build_type == "Debug" else "0",
                        dll="1" if self.options.shared else "0",
                        cflags=" ".join(autotools.flags + extra_flags),
                        cxxflags=" ".join(autotools.cxx_flags + extra_flags),
                        ldflags=" ".join(autotools.link_flags),
                    ))

        with tools.files.chdir(self, libmpdec_folder):
            shutil.copy("mpdecimal.h", dist_folder)
            if self.options.shared:
                shutil.copy("libmpdec-{}.dll".format(self.version), os.path.join(dist_folder, "libmpdec-{}.dll".format(self.version)))
                shutil.copy("libmpdec-{}.dll.exp".format(self.version), os.path.join(dist_folder, "libmpdec-{}.exp".format(self.version)))
                shutil.copy("libmpdec-{}.dll.lib".format(self.version), os.path.join(dist_folder, "libmpdec-{}.lib".format(self.version)))
            else:
                shutil.copy("libmpdec-{}.lib".format(self.version), os.path.join(dist_folder, "libmpdec-{}.lib".format(self.version)))
        if self.options.cxx:
            with tools.files.chdir(self, libmpdecpp_folder):
                shutil.copy("decimal.hh", dist_folder)
                shutil.copy("libmpdec++-{}.lib".format(self.version), os.path.join(dist_folder, "libmpdec++-{}.lib".format(self.version)))

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_vars = self._autotools.vars
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            conf_vars["LDFLAGS"] += " -arch arm64"
            conf_vars["LDXXFLAGS"] = "-arch arm64"
        conf_args = [
            "--enable-cxx" if self.options.cxx else "--disable-cxx"
        ]
        self._autotools.configure(args=conf_args, vars=conf_vars)
        return self._autotools

    @property
    def _shared_suffix(self):
        if tools.apple.is_apple_os(self, self.settings.os):
            return ".dylib"
        return {
            "Windows": ".dll",
        }.get(str(self.settings.os), ".so")

    @property
    def _target_names(self):
        libsuffix = self._shared_suffix if self.options.shared else ".a"
        versionsuffix = ".{}".format(self.version) if self.options.shared else ""
        suffix = "{}{}".format(versionsuffix, libsuffix) if tools.apple.is_apple_os(self, self.settings.os) or self.settings.os == "Windows" else "{}{}".format(libsuffix, versionsuffix)
        return "libmpdec{}".format(suffix), "libmpdec++{}".format(suffix)

    def build(self):
        self._patch_sources()
        if self._is_msvc:
            self._build_msvc()
        else:
            with tools.files.chdir(self, self._source_subfolder):
                self.run("autoreconf -fiv", win_bash=tools.os_info.is_windows)
                autotools = self._configure_autotools()
                self.output.info(tools.files.load(self, os.path.join("libmpdec", "Makefile")))
                libmpdec, libmpdecpp = self._target_names
                with tools.files.chdir(self, "libmpdec"):
                    autotools.make(target=libmpdec)
                if self.options.cxx:
                    with tools.files.chdir(self, "libmpdec++"):
                        autotools.make(target=libmpdecpp)

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        if self._is_msvc:
            distfolder = os.path.join(self.build_folder, self._source_subfolder, "vcbuild", "dist{}".format(32 if self.settings.arch == "x86" else 64))
            self.copy("vc*.h", src=os.path.join(self.build_folder, self._source_subfolder, "libmpdec"), dst="include")
            self.copy("*.h", src=distfolder, dst="include")
            if self.options.cxx:
                self.copy("*.hh", src=distfolder, dst="include")
            self.copy("*.lib", src=distfolder, dst="lib")
            self.copy("*.dll", src=distfolder, dst="bin")
        else:
            mpdecdir = os.path.join(self._source_subfolder, "libmpdec")
            mpdecppdir = os.path.join(self._source_subfolder, "libmpdec++")
            self.copy("mpdecimal.h", src=mpdecdir, dst="include")
            if self.options.cxx:
                self.copy("decimal.hh", src=mpdecppdir, dst="include")
            builddirs = [mpdecdir]
            if self.options.cxx:
                builddirs.append(mpdecppdir)
            for builddir in builddirs:
                self.copy("*.a", src=builddir, dst="lib")
                self.copy("*.so", src=builddir, dst="lib")
                self.copy("*.so.*", src=builddir, dst="lib")
                self.copy("*.dylib", src=builddir, dst="lib")
                self.copy("*.dll", src=builddir, dst="bin")

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
                if tools.scm.Version(self, self.version) >= "2.5.1":
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
                if tools.scm.Version(self, self.version) >= "2.5.1":
                    self.cpp_info.components["libmpdecimal"].defines = ["MPDECIMALXX_DLL"]
