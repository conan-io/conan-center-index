from conan import ConanFile
from conan.tools.files import chdir, copy, get, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import msvs_toolset
import os


required_conan_version = ">=1.54.0"

class PerlConan(ConanFile):
    name = "perl"
    description = "A high-level, general-purpose, interpreted, dynamic programming language"
    license = "GPL-1.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.perl.org/"
    topics = ("scripting", "programming", "language")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("bzip2/1.0.8")
        self.requires("zlib/[>=1.2.11 <2]")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()
    
    @property
    def _compiler(self):
        compilers = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict)
        if "c" in compilers:
            return compilers["c"]
        
        # Otherwise it will use the system "cc" command - assuming the profile reflects this.
        return None

    @property
    def _cctype(self):
        return f"MSVC{msvs_toolset(self)}"

    def build(self):
        if self.settings.os == "Windows":
            # TODO: MinGW, maybe look into GNUMakefile in the same directory
            makefile_dir = os.path.join(self.source_folder, "win32")
            makefile = os.path.join(makefile_dir, "Makefile")
            # Fix calls to 'rename' giving wrong syntax. 'ren' on Windows is synonymous with 'rename',
            # 'rename' in bash is something completely different.
            replace_in_file(self, makefile, "rename", "ren")
            # Specify installation directory: These are set with equals in the makefile so
            # they must be modified else any provided value will be overwritten.
            replace_in_file(self, makefile, "INST_DRV\t= c:", f"INST_DRV\t= {self.package_folder}")
            replace_in_file(self, makefile, "INST_TOP\t= $(INST_DRV)\perl", f"INST_TOP\t= {self.package_folder}")

            with chdir(self, os.path.join(self.source_folder, "win32")):
                # Errors if info about the MSVC version isn't given.
                os.environ["CCTYPE"] = self._cctype
                # Must use nmake, otherwise the build hangs
                self.run("nmake")
        else:
            # Can't use configure() since Perl uses "Configure" instead of "configure". Renaming the file does not seem to work.
            with chdir(self, self.source_folder):
                command = f"./Configure -de -Dprefix={self.package_folder}"
                compiler = self._compiler
                if compiler:
                    command += f" -Dcc={compiler}"
                self.run(command)
                autotools = Autotools(self)
                autotools.make()

    def package(self):
        copy(self, "Copying", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if self.settings.os == "Windows":
            with chdir(self, os.path.join(self.source_folder, "win32")):
                os.environ["CCTYPE"] = self._cctype
                self.run(f"nmake install")
        else:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.install(args=["DESTDIR="])

        rmdir(self, os.path.join(self.package_folder, "man"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "rt"]

        self.runenv_info.define_path("PERL5LIB", os.path.join(self.package_folder, "lib"))

        # TODO: Legacy, to be removed in Conan 2.0
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.PERL5LIB = os.path.join(self.package_folder, "lib")

    def package_id(self):
        del self.info.settings.compiler
