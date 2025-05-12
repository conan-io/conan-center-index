import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeToolchain

required_conan_version = ">=1.53.0"


class LibisalConan(ConanFile):
    name = "isa-l"
    description = "Intel's Intelligent Storage Acceleration Library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/intel/isa-l"
    topics = "compression"
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
        return getattr(self, "settings_build", self.settings)

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
        if self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration(f"{self.settings.arch} architecture is not supported")
        if self.version == "2.30.0" and self._settings_build.arch == "armv8":
            raise ConanInvalidConfiguration(f"Version {self.version} does not support armv8")

    def build_requirements(self):
        self.tool_requires("nasm/2.15.05")
        if not is_msvc(self):
            self.tool_requires("libtool/2.4.7")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            # ./configure bugs out if $AS executable has an absolute path
            env = tc.environment()
            env.define("AS", "nasm")
            tc.generate(env)

    def build(self):
        with chdir(self, self.source_folder):
            if is_msvc(self):
                replace_in_file(self, "Makefile.nmake",
                                " static" if self.options.shared else " dll", "")
                self.run("nmake /f Makefile.nmake")
            else:
                autotools = Autotools(self)
                autotools.autoreconf()
                autotools.configure()
                autotools.make()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*/isa-l.h",
             dst=os.path.join(self.package_folder, "include/isa-l"),
             src=self.source_folder,
             keep_path=False)
        copy(self, "*.h",
             dst=os.path.join(self.package_folder, "include/isa-l"),
             src=os.path.join(self.source_folder, "include"),
             keep_path=False)
        copy(self, "*.dll",
             dst=os.path.join(self.package_folder, "bin"),
             src=self.source_folder,
             keep_path=False)
        for pattern in ["*.so*", "*.dylib", "*.lib", "*.a"]:
            copy(self, pattern,
                 dst=os.path.join(self.package_folder, "lib"),
                 src=self.source_folder,
                 keep_path=False)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libisal")
        if is_msvc(self):
            suffix = "" if self.options.shared else "_static"
            self.cpp_info.libs = [f"isa-l{suffix}"]
        else:
            self.cpp_info.libs = ["isal"]
