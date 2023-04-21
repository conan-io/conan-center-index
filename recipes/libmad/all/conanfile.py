from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rm
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"


class LibmadConan(ConanFile):
    name = "libmad"
    description = "MAD is a high-quality MPEG audio decoder."
    topics = ("mad", "MPEG", "audio", "decoder")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.underbit.com/products/mad/"
    license = "GPL-2.0-or-later"
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

    exports_sources = "CMakeLists.txt"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        if is_msvc(self):
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("gnu-config/cci.20210814")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = CMakeToolchain(self)
            tc.variables["LIBMAD_SRC_DIR"] = self.source_folder.replace("\\", "/")
            tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            tc = AutotoolsToolchain(self)
            tc.generate()

    def build(self):
        if is_msvc(self):
            replace_in_file(
                self, os.path.join(self.source_folder, "msvc++", "mad.h"),
                "# define FPM_INTEL", "# define FPM_DEFAULT",
            )
            cmake = CMake(self)
            cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
            cmake.build()
        else:
            for gnu_config in [
                self.conf.get("user.gnu-config:config_guess", check_type=str),
                self.conf.get("user.gnu-config:config_sub", check_type=str),
            ]:
                if gnu_config:
                    copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=self.source_folder)
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        for license_file in ("COPYRIGHT", "COPYING", "CREDITS"):
            copy(self, license_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            cmake = CMake(self)
            cmake.install()
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["libmad" if is_msvc(self) else "mad"]
