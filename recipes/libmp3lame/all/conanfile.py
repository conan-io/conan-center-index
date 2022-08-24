from conan.tools.files import rename
from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
from contextlib import contextmanager
import functools
import os
import shutil

required_conan_version = ">=1.33.0"


class LibMP3LameConan(ConanFile):
    name = "libmp3lame"
    url = "https://github.com/conan-io/conan-center-index"
    description = "LAME is a high quality MPEG Audio Layer III (MP3) encoder licensed under the LGPL."
    homepage = "http://lame.sourceforge.net"
    topics = ("libmp3lame", "multimedia", "audio", "mp3", "decoder", "encoding", "decoding")
    license = "LGPL-2.0"

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
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _is_clang_cl(self):
        return str(self.settings.compiler) in ["clang"] and str(self.settings.os) in ['Windows']

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if not self._is_msvc and not self._is_clang_cl:
            self.build_requires("gnu-config/cci.20201022")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _apply_patch(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "include", "libmp3lame.sym"), "lame_init_old\n", "")

    @contextmanager
    def _msvc_build_environment(self):
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self.settings):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    yield

    def _build_vs(self):
        with self._msvc_build_environment():
            shutil.copy("configMS.h", "config.h")
            # Honor vc runtime
            tools.replace_in_file("Makefile.MSVC", "CC_OPTS = $(CC_OPTS) /MT", "")
            # Do not hardcode LTO
            tools.replace_in_file("Makefile.MSVC", " /GL", "")
            tools.replace_in_file("Makefile.MSVC", " /LTCG", "")
            tools.replace_in_file("Makefile.MSVC", "ADDL_OBJ = bufferoverflowU.lib", "")
            command = "nmake -f Makefile.MSVC comp=msvc"
            if self._is_clang_cl:
                cl = os.environ.get('CC', "clang-cl")
                link = os.environ.get("LD", 'lld-link')
                tools.replace_in_file('Makefile.MSVC', 'CC = cl', 'CC = %s' % cl)
                tools.replace_in_file('Makefile.MSVC', 'LN = link', 'LN = %s' % link)
                # what is /GAy? MSDN doesn't know it
                # clang-cl: error: no such file or directory: '/GAy'
                # https://docs.microsoft.com/en-us/cpp/build/reference/ga-optimize-for-windows-application?view=msvc-170
                tools.replace_in_file('Makefile.MSVC', '/GAy', '/GA')
            if self.settings.arch == "x86_64":
                tools.replace_in_file("Makefile.MSVC", "MACHINE = /machine:I386", "MACHINE =/machine:X64")
                command += " MSVCVER=Win64 asm=yes"
            elif self.settings.arch == "armv8":
                tools.replace_in_file("Makefile.MSVC", "MACHINE = /machine:I386", "MACHINE =/machine:ARM64")
                command += " MSVCVER=Win64"
            else:
                command += " asm=yes"
            command += " libmp3lame.dll" if self.options.shared else " libmp3lame-static.lib"
            self.run(command)

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--disable-frontend",
        ]
        if self.settings.build_type == "Debug":
            args.append("--enable-debug")
        if self.settings.compiler == "clang" and self.settings.arch in ["x86", "x86_64"]:
            autotools.flags.extend(["-mmmx", "-msse"])
        autotools.configure(args=args, configure_dir=self._source_subfolder)
        return autotools

    def _build_autotools(self):
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config.guess"))
        tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                              "-install_name \\$rpath/",
                              "-install_name @rpath/")
        autotools = self._configure_autotools()
        autotools.make()

    def build(self):
        self._apply_patch()
        if self._is_msvc or self._is_clang_cl:
            self._build_vs()
        else:
            self._build_autotools()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        if self._is_msvc or self._is_clang_cl:
            self.copy(pattern="*.h", src=os.path.join(self._source_subfolder, "include"), dst=os.path.join("include", "lame"))
            name = "libmp3lame.lib" if self.options.shared else "libmp3lame-static.lib"
            self.copy(name, src=os.path.join(self._source_subfolder, "output"), dst="lib")
            if self.options.shared:
                self.copy(pattern="*.dll", src=os.path.join(self._source_subfolder, "output"), dst="bin")
            rename(self, os.path.join(self.package_folder, "lib", name),
                         os.path.join(self.package_folder, "lib", "mp3lame.lib"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = ["mp3lame"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
