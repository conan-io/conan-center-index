from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rm
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os

required_conan_version = ">=1.57.0"

class LiquidDspConan(ConanFile):
    name = "liquid-dsp"
    description = "Digital signal processing library for software-defined radios (and more)"
    topics = ("dsp", "sdr")
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jgaeddert/liquid-dsp"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "simdoverride": [True, False],
        "with_fftw": [True, False],
    }
    default_options = {
        "shared": False,
        "simdoverride": True,
        "with_fftw": False,
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        if self.options.with_fftw:
            self.requires("fftw/[~3.3]")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")
            
    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross building is not yet supported. Contributions are welcome")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        configure_args = {}

        # configure script does not support shared or static library flags
        for arg in ["--enable-shared", "--disable-static", "--disable-shared", "--enable-static"]:
            configure_args[arg] = None

        if not self.options.with_fftw:
            configure_args["--enable-fftoverride"] = ''
        if self.options.simdoverride:
            configure_args["--enable-simdoverride"] = ''
        tc.update_configure_args(configure_args)

        env = tc.environment()
        if is_msvc(self):
            compile_wrapper = unix_path(self, self.conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, self.conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)

        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()

        rm(self, "*.a" if self.options.shared else "*.[so|dylib]*", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["liquid"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
