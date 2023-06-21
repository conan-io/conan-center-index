from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.54.0"


class LibevConan(ConanFile):
    name = "libev"
    description = "A full-featured and high-performance event loop that is loosely modelled after libevent"
    topics = ("event", "event-loop", "periodic-timer", "notify")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://software.schmorp.de/pkg/libev.html"
    license = ["BSD-2-Clause", "GPL-2.0-or-later"]

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

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, dst=self.export_sources_folder)
        copy(self, "config.h", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os == "Windows" and not is_msvc(self) and self.options.shared:
            # libtool:   error: can't build i686-pc-mingw32 shared library unless -no-undefined is specified
            raise ConanInvalidConfiguration(f"{self.ref} can't be built as shared on Windows without Visual Studio")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self):
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = CMakeToolchain(self)
            tc.variables["EV_SRC_DIR"] = self.source_folder.replace("\\", "/")
            tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            tc = AutotoolsToolchain(self)
            tc.generate()

    def build(self):
        if is_msvc(self):
            base_folder = os.path.join(self.source_folder, os.pardir)
            copy(self, "config.h", src=base_folder, dst=self.source_folder)
            cmake = CMake(self)
            cmake.configure(build_script_folder=base_folder)
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            cmake = CMake(self)
            cmake.install()
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "share"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["ev"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
