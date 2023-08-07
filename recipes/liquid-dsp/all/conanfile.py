import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import Environment
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rename
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

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
        copy(self, "generate_link_library.bat", src=self.recipe_folder, dst=self.export_sources_folder)

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

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("mingw-w64/8.0.2")
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.extra_cflags += ["-static-libgcc"]
        if self.settings.build_type == "Debug":
            tc.configure_args.append("--enable-debug-messages")
            tc.extra_cflags += ["-g", "-O0"]
        else:
            tc.extra_cflags += ["-s", "-O2", "-DNDEBUG"]
        if self.options.simdoverride:
            tc.configure_args.append("--enable-simdoverride")
        tc.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f'{ar_wrapper} "lib -nologo"')
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def _patch_sources(self):
        if self.settings.os == "Windows":
            apply_conandata_patches(self)

    def _gen_link_library(self):
        if is_msvc(self) and self.options.shared:
            self.run("cmd /c generate_link_library.bat")
            with chdir(self, self.source_folder):
                self.run("{} /def:libliquid.def /out:libliquid.lib /machine:{}".format(
                    os.getenv("AR"), "X86" if self.settings.arch == "x86" else "X64")
                )

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
            self.run("./bootstrap.sh")
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

    def package_info(self):
        self.cpp_info.libs = [self._libname]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
