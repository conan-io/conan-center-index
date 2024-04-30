from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os


required_conan_version = ">=1.54.0"

class PackageConan(ConanFile):
    name = "git"
    description = "Fast, scalable, distributed revision control system"
    license = "GPL-2.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git-scm.com/"
    topics = ("scm", "version-control")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
#    options = {
#        "shared": [True, False],
#        "fPIC": [True, False],
        #"with_foobar": [True, False],
#    }
#    default_options = {
#        "shared": False,
#        "fPIC": True,
        #"with_foobar": True,
#    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

#    def config_options(self):
#        if self.settings.os == "Windows":
#            del self.options.fPIC

    def configure(self):
        # Since this an an application
        self.settings.rm_safe("compiler")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("expat/[>=2.6.2 <3]") #TODO
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("libiconv/1.17") #TODO
        self.requires("openssl/[>=1.1 <4]")
        self.requires("pcre2/10.43")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        self.tool_requires("gettext/0.22.5")
        # required to suppport windows as a build machine
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        # for msvc support to get compile & ar-lib scripts (may be avoided if shipped in source code of the library)
        # not needed if libtool already in build requirements
        #if is_msvc(self):
        #    self.tool_requires("automake/x.y.z")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        # autotools usually uses 'yes' and 'no' to enable/disable options
#        def yes_no(v): return "yes" if v else "no"
        print(self.dependencies['openssl'].package_folder)
        tc.configure_args.extend([
            f"--with-openssl={self.dependencies['openssl'].package_folder}",
            f"--with-curl={self.dependencies['libcurl'].package_folder}",
            f"--with-libpcre2={self.dependencies['pcre2'].package_folder}",
            # This could probably easily be supported as an option, but it would likely never be useful in a conan recipe.
            "--with-tcltk=no"
        ])
        tc.generate()

        # If Visual Studio is supported
#        if is_msvc(self):
#            env = Environment()
#            # get compile & ar-lib from automake (or eventually lib source code if available)
#            # it's not always required to wrap CC, CXX & AR with these scripts, it depends on how much love was put in
#            # upstream build files
#            automake_conf = self.dependencies.build["automake"].conf_info
#            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
#            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
#            env.define("CC", f"{compile_wrapper} cl -nologo")
#            env.define("CXX", f"{compile_wrapper} cl -nologo")
#            env.define("LD", "link -nologo")
#            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
#            env.define("NM", "dumpbin -symbols")
#            env.define("OBJDUMP", ":")
#            env.define("RANLIB", ":")
#            env.define("STRIP", ":")
#            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        os.chdir(self.source_folder)
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        # Probably will never be needed for the sake of a Conan recipe.
        # TODO: Is there a cleaner way to do this?
        os.environ["NO_GITWEB"] = "1"
        autotools.make()

    def package(self):
        os.chdir(self.source_folder)
        autotools = Autotools(self)
        autotools.install()

        # "share" folder exists, but is probably fine to keep *no large files). Will investigate the contents.

    def package_info(self):
        self.runenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))
