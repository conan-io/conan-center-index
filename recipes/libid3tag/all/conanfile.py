import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import cross_building
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, rm, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class LibId3TagConan(ConanFile):
    name = "libid3tag"
    description = "ID3 tag manipulation library."
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.underbit.com/products/mad/"
    topics = ("mad", "id3", "MPEG", "audio", "decoder")

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

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        if is_msvc(self):
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")

    def validate_build(self):
        if cross_building(self) and is_apple_os(self) and self.options.shared:
            # Cannot cross-build due to a very old version of libtool that does not 
            # correctly propagate `-sysroot` or `-arch` when creating a shared library
            raise ConanInvalidConfiguration("Shared library cross-building is not supported on Apple platforms")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("gnu-config/cci.20210814")
            if self.settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = CMakeToolchain(self)
            tc.preprocessor_definitions["ID3TAG_EXPORT"] = "__declspec(dllexport)" if self.options.shared else ""
            tc.generate()
            deps = CMakeDeps(self)
            deps.generate()
        else:
            venv = VirtualBuildEnv(self)
            venv.generate()
            tc = AutotoolsToolchain(self)
            tc.generate()
            deps = AutotoolsDeps(self)
            deps.generate()

    def build(self):
        if is_msvc(self):
            # https://github.com/markjeee/libid3tag/blob/master/id3tag.h#L355-L358
            replace_in_file(self, os.path.join(self.source_folder, "id3tag.h"),
                            "extern char", "ID3TAG_EXPORT extern char")
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            for gnu_config in [
                self.conf.get("user.gnu-config:config_guess", check_type=str),
                self.conf.get("user.gnu-config:config_sub", check_type=str),
            ]:
                if gnu_config:
                    copy(self, os.path.basename(gnu_config), os.path.dirname(gnu_config), self.source_folder)
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.configure()
                autotools.make()

    def package(self):
        for license_file in ["COPYRIGHT", "COPYING", "CREDITS"]:
            copy(self, license_file, self.source_folder, os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            cmake = CMake(self)
            cmake.install()
        else:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.install()
            rm(self, "*.la", self.package_folder, recursive=True)
            fix_apple_shared_install_name(self)

    def package_info(self):
        if is_msvc(self):
            self.cpp_info.libs = ["libid3tag"]
            self.cpp_info.defines.append("ID3TAG_EXPORT=" + ("__declspec(dllimport)" if self.options.shared else ""))
        else:
            self.cpp_info.libs = ["id3tag"]
