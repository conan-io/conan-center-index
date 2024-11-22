import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import chdir, copy, get, rename
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class LiquidDspConan(ConanFile):
    name = "liquid-dsp"
    description = "Digital signal processing library for software-defined radios (and more)"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jgaeddert/liquid-dsp"
    topics = ("dsp", "sdr")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "simdoverride": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "simdoverride": False,
    }

    @property
    def _target_name(self):
        if is_apple_os(self):
            if not self.options.shared:
                return "libliquid.ar"
            return "libliquid.dylib"
        if not self.options.shared:
            return "libliquid.a"
        return "libliquid.so"

    @property
    def _lib_pattern(self):
        if is_apple_os(self) and not self.options.shared:
            return "libliquid.a"
        return self._target_name

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if cross_building(self):
            raise ConanInvalidConfiguration("Cross building is not yet supported. Contributions are welcome")
        if is_msvc(self):
            raise ConanInvalidConfiguration("MSVC is not supported due to missing 'complex' data type support")

    def build_requirements(self):
        # For ./bootstrap.sh
        self.tool_requires("autoconf/2.71")
        self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        gcc_env = Environment()
        if self.settings.build_type == "Debug":
            cflags = "-g -O0"
        else:
            cflags = "-s -O2 -DNDEBUG"
        gcc_env.append("CFLAGS", cflags)
        gcc_env.vars(self, scope="gcc").save_script("conan_gcc_env")

        tc = AutotoolsToolchain(self)
        if self.settings.build_type == "Debug":
            tc.configure_args.append("--enable-debug-messages")
        if self.options.simdoverride:
            tc.configure_args.append("--enable-simdoverride")
        tc.generate(gcc_env)

    def _rename_libraries(self):
        with chdir(self, self.source_folder):
            if is_apple_os(self) and not self.options.shared:
                rename(self, "libliquid.ar", "libliquid.a")

    def build(self):
        with chdir(self, self.source_folder):
            self.run("./bootstrap.sh", env=["conanbuild", "gcc"])
            autotools = Autotools(self)
            autotools.configure()
            autotools.make(self._target_name)
        self._rename_libraries()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "liquid.h",
             dst=os.path.join(self.package_folder, "include", "liquid"),
             src=os.path.join(self.source_folder, "include"))
        copy(self, self._lib_pattern,
             dst=os.path.join(self.package_folder, "lib"),
             src=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = ["liquid"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
