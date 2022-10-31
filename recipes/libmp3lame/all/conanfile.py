from conan import ConanFile
from conan.tools.microsoft import is_msvc, VCVars, unix_path
from conan.tools.files import export_conandata_patches, apply_conandata_patches, get, chdir, rmdir, copy, rm, replace_in_file, rename
from conan.tools.layout import basic_layout
from conan.tools.gnu import Autotools, AutotoolsToolchain
import os
import shutil

required_conan_version = ">=1.52.0"


class LibMP3LameConan(ConanFile):
    name = "libmp3lame"
    url = "https://github.com/conan-io/conan-center-index"
    description = "LAME is a high quality MPEG Audio Layer III (MP3) encoder licensed under the LGPL."
    homepage = "http://lame.sourceforge.net"
    topics = "multimedia", "audio", "mp3", "decoder", "encoding", "decoding"
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
    def _is_clang_cl(self):
        return str(self.settings.compiler) in ["clang"] and str(self.settings.os) in ['Windows']

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
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if not is_msvc(self) and not self._is_clang_cl:
            self.build_requires("gnu-config/cci.20201022")
            if self.settings.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)


    def _generate_vs(self):
        tc = VCVars(self)
        tc.generate()

    def _build_vs(self):
        with chdir(self, self.source_folder):
            shutil.copy2("configMS.h", "config.h")
            # Honor vc runtime
            replace_in_file(self, "Makefile.MSVC", "CC_OPTS = $(CC_OPTS) /MT", "")
            # Do not hardcode LTO
            replace_in_file(self, "Makefile.MSVC", " /GL", "")
            replace_in_file(self, "Makefile.MSVC", " /LTCG", "")
            replace_in_file(self, "Makefile.MSVC", "ADDL_OBJ = bufferoverflowU.lib", "")
            command = "nmake -f Makefile.MSVC comp=msvc"
            if self._is_clang_cl:
                cl = os.environ.get('CC', "clang-cl")
                link = os.environ.get("LD", 'lld-link')
                replace_in_file(self, 'Makefile.MSVC', 'CC = cl', 'CC = %s' % cl)
                replace_in_file(self, 'Makefile.MSVC', 'LN = link', 'LN = %s' % link)
                # what is /GAy? MSDN doesn't know it
                # clang-cl: error: no such file or directory: '/GAy'
                # https://docs.microsoft.com/en-us/cpp/build/reference/ga-optimize-for-windows-application?view=msvc-170
                replace_in_file(self, 'Makefile.MSVC', '/GAy', '/GA')
            if self.settings.arch == "x86_64":
                replace_in_file(self, "Makefile.MSVC", "MACHINE = /machine:I386", "MACHINE =/machine:X64")
                command += " MSVCVER=Win64 asm=yes"
            elif self.settings.arch == "armv8":
                replace_in_file(self, "Makefile.MSVC", "MACHINE = /machine:I386", "MACHINE =/machine:ARM64")
                command += " MSVCVER=Win64"
            else:
                command += " asm=yes"
            command += " libmp3lame.dll" if self.options.shared else " libmp3lame-static.lib"
            self.run(command)

    def _generate_autotools(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--disable-frontend")
        if self.settings.compiler == "clang" and self.settings.arch in ["x86", "x86_64"]:
            tc.extra_cxxflags.extend(["-mmmx", "-msse"])
        tc.generate()

    def _build_autotools(self):
        copy(self, "config.sub", self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self.source_folder))
        copy(self, "config.guess", self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self.source_folder))
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def generate(self):
        if is_msvc(self) or self._is_clang_cl:
            self._generate_vs()
        else:
            self._generate_autotools()

    def build(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "include", "libmp3lame.sym"), "lame_init_old\n", "")

        if is_msvc(self) or self._is_clang_cl:
            self._build_vs()
        else:
            self._build_autotools()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder,"licenses"))
        if is_msvc(self) or self._is_clang_cl:
            copy(self, pattern="*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder,"include", "lame"))
            name = "libmp3lame.lib" if self.options.shared else "libmp3lame-static.lib"
            copy(self, name, src=os.path.join(self.source_folder, "output"), dst=os.path.join(self.package_folder,"lib"))
            if self.options.shared:
                copy(self, pattern="*.dll", src=os.path.join(self.source_folder, "output"), dst=os.path.join(self.package_folder,"bin"))
            rename(self, os.path.join(self.package_folder, "lib", name),
                         os.path.join(self.package_folder, "lib", "mp3lame.lib"))
        else:
            autotools = Autotools(self)
            # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
            autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
            rmdir(self, os.path.join(self.package_folder, "share"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["mp3lame"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
