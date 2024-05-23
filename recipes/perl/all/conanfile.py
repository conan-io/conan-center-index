from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import chdir, copy, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
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

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}. "
                                            "You may want to use strawberryperl instead.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("bzip2/1.0.8")
        self.requires("zlib/[>=1.2.11 <2]")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()
    
    @property
    def _compiler(self):
        compilers = self.conf.get("tools.build:compiler_executables", default={},
                                                     check_type=dict)
        if "c" in compilers:
            return compilers["c"]
        
        # Otherwise it will use the system "cc" command - assuming the profile reflects this.
        return None

    def build(self):
        # Can't use configure() since Perl uses "Configure" instead of "configure". Renaming the file does not seem to work.
        with chdir(self, self.source_folder):
            config_path = os.path.join(self.source_folder, 'Configure')
            command = f"{config_path} -de -Dprefix={self.package_folder}"
            compiler = self._compiler
            if compiler:
                command += f" -Dcc={compiler}"
            self.run(command)
            autotools = Autotools(self)
            autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install(args=["DESTDIR="])

        rmdir(self, os.path.join(self.package_folder, "man"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        # TODO: Legacy, to be removed in Conan 2.0
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

    def package_id(self):
        del self.info.settings.compiler
