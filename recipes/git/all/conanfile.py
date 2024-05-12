from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.env import VirtualBuildEnv, Environment
from conan.tools.files import get, replace_in_file
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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        # C only
        self.settings.compiler.rm_safe("libcxx")
        self.settings.compiler.rm_safe("cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("expat/[>=2.6.2 <3]")
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("libiconv/1.17")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("pcre2/10.43")
        self.requires("zlib/[>=1.2.11 <2]")

        # might need perl

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("gettext/0.22.5")
    
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = CMakeToolchain(self)
            # FIXME
            tc.generator = "Ninja"
            tc.generate()

            deps = CMakeDeps(self)
            deps.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()

            env = Environment()
            def package_folder_of(lib): return self.dependencies[lib].package_folder.replace('\\', '/')
            env.define("ZLIB_PATH", package_folder_of('zlib'))
            env.define("EXPATDIR", package_folder_of('expat'))
            env.define("CURLDIR", package_folder_of('libcurl'))
            env.define("LIBPCREDIR", package_folder_of('pcre2'))
            env.define("OPENSSLDIR", package_folder_of('openssl'))
            env.define("ICONVDIR", package_folder_of('libiconv'))

            env.vars(self).save_script("conanbuild_msvc")

            tc = AutotoolsToolchain(self)
            tc.generate()

    def build(self):
        if is_msvc(self):
            cmake_directory = os.path.join(self.source_folder, "contrib", "buildsystems")
            cmake_file = os.path.join(cmake_directory, "CMakeLists.txt")
            replace_in_file(self, cmake_file, "${EXPAT_LIBRARIES}", "expat::expat")

            replace_in_file(self, cmake_file, "if(EXPAT_VERSION_STRING VERSION_LESS_EQUAL 1.2)", "if(FALSE)")
            cmake = CMake(self)
            cmake.configure(
                build_script_folder=cmake_directory,
                # USE_VCPKG is checked before project(), so it can't be injected from the toolchain.
                cli_args=["-DUSE_VCPKG=OFF"],
                
            )
            cmake.build()
        else:
            os.chdir(self.source_folder)
            replace_in_file(self, os.path.join(self.source_folder, "git-compat-util.h"), '#error "Required C99 support is in a test phase.', '//')
            autotools = Autotools(self)
            # Probably will never be needed for the sake of a Conan recipe.
            # TODO: Is there a cleaner way to do this?
            os.environ["NO_GITWEB"] = "1"
            autotools.make()

    def package(self):
        if is_msvc(self):
            cmake = CMake(self)
            cmake.install()
        else:
            os.chdir(self.source_folder)
            autotools = Autotools(self)
            autotools.install()
            # "share" folder exists, but is probably fine to keep *no large files). Will investigate the contents.

    def package_id(self):
        # Just an application
        del self.info.settings.compiler

    def package_info(self):
        self.runenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))

        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
