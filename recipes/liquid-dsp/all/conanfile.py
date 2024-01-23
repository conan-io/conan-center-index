import os
from io import StringIO

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rename
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
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _libname(self):
        if self.settings.os == "Windows":
            return "libliquid"
        return "liquid"

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
        if self.settings.os != "Windows":
            return self._target_name
        return "libliquid.lib"

    def export_sources(self):
        export_conandata_patches(self)

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
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross building is not yet supported. Contributions are welcome")
        if is_msvc(self) and not self.options.shared:
            # Only managed to get it building locally with static libgcc, which adds GPL license restrictions.
            # __getreent and fprintf were not found in CI.
            raise ConanInvalidConfiguration("Static builds are not supported on MSVC.")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            if is_msvc(self):
                # GCC from MinGW is used due to MSVC C99 not supporting complex float
                self.tool_requires("mingw-builds/12.2.0")
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        # For ./bootstrap.sh
        self.tool_requires("autoconf/2.71")
        self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        if not cross_building(self):
            venv = VirtualRunEnv(self)
            venv.generate(scope="build")

        gcc_env = Environment()
        if is_msvc(self):
            gcc_env.define("CC", "gcc")
            gcc_env.define("CXX", "g++")
            gcc_env.define("LD", "ld")
            gcc_env.define("AR", "ar")
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

    def _patch_sources(self):
        if self.settings.os == "Windows":
            apply_conandata_patches(self)

    def _gen_link_library(self):
        if is_msvc(self) and self.options.shared:
            with chdir(self, self.source_folder):
                stdout = StringIO()
                self.run("dumpbin -EXPORTS libliquid.dll", stdout)
                lines = stdout.getvalue().splitlines()
                with open("libliquid.def", "w", encoding="ascii") as f:
                    f.write("EXPORTS\n")
                    for line in lines[19:]:
                        tokens = line.split()
                        if len(tokens) > 3:
                            f.write(tokens[3] + "\n")
                arch = "X86" if self.settings.arch == "x86" else "X64"
                self.run(f"lib /def:libliquid.def /out:libliquid.lib /machine:{arch}")

    def _rename_libraries(self):
        with chdir(self, self.source_folder):
            if self.settings.os == "Windows" and self.options.shared:
                rename(self, "libliquid.so", "libliquid.dll")
            elif self.settings.os == "Windows" and not self.options.shared:
                rename(self, "libliquid.a", "libliquid.lib")
            elif is_apple_os(self) and not self.options.shared:
                rename(self, "libliquid.ar", "libliquid.a")

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            self.run("./bootstrap.sh", env=["conanbuild", "gcc"])
            autotools = Autotools(self)
            autotools.configure()
            autotools.make(self._target_name)
        self._rename_libraries()
        self._gen_link_library()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "liquid.h",
             dst=os.path.join(self.package_folder, "include", "liquid"),
             src=os.path.join(self.source_folder, "include"))
        copy(self, "libliquid.dll",
             dst=os.path.join(self.package_folder, "bin"),
             src=self.source_folder)
        copy(self, self._lib_pattern,
             dst=os.path.join(self.package_folder, "lib"),
             src=self.source_folder)

        if is_msvc(self):
            # Package MinGW runtime libraries since Conan lacks support for proper handling of compiler runtime libs
            mingw = self.dependencies.build["mingw-builds"].package_folder
            if self.options.shared:
                copy(self, "libgcc_s*.dll", os.path.join(mingw, "bin"), os.path.join(self.package_folder, "bin"), keep_path=False)
                copy(self, "libgcc_s.a", os.path.join(mingw, "lib", "gcc", f"{self.settings.arch}-w64-mingw32", "lib"), os.path.join(self.package_folder, "lib"))
            else:
                copy(self, "libgcc.a", os.path.join(mingw, "lib", "gcc", f"{self.settings.arch}-w64-mingw32", "12.2.0"), os.path.join(self.package_folder, "lib"))
            copy(self, "libmingwex.a", os.path.join(mingw, f"{self.settings.arch}-w64-mingw32", "lib"), os.path.join(self.package_folder, "lib"))
            for lib in ["libgcc", "libgcc_s", "libmingwex"]:
                if os.path.exists(os.path.join(self.package_folder, "lib", f"{lib}.a")):
                    rename(self, os.path.join(self.package_folder, "lib", f"{lib}.a"),
                           os.path.join(self.package_folder, "lib", f"{lib}.lib"))

    def package_info(self):
        self.cpp_info.libs = [self._libname]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        if is_msvc(self):
            if self.options.shared:
                self.cpp_info.libs.append("libgcc_s")
            else:
                self.cpp_info.libs.append("libgcc")
            self.cpp_info.libs.append("libmingwex")
