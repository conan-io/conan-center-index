from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os

required_conan_version = ">=1.52.0"


class YASMConan(ConanFile):
    name = "yasm"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yasm/yasm"
    description = "Yasm is a complete rewrite of the NASM assembler under the 'new' BSD License"
    topics = ("yasm", "installer", "assembler")
    license = "BSD-2-Clause"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        if is_msvc(self):
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self):
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version][0],
                  destination=self.source_folder, strip_root=True)

    def _generate_autotools(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        enable_debug = "yes" if self.settings.build_type == "Debug" else "no"
        tc.configure_args.extend([
            f"--enable-debug={enable_debug}",
            "--disable-rpath",
            "--disable-nls",
        ])
        tc.generate()

    def _generate_cmake(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["YASM_BUILD_TESTS"] = False
        tc.generate()

    def generate(self):
        if is_msvc(self):
            self._generate_cmake()
        else:
            self._generate_autotools()

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, pattern="BSD.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "include"))
            rmdir(self, os.path.join(self.package_folder, "lib"))
        else:
            autotools = Autotools(self)
            # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
            autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
