import os

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rmdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class Re2CConan(ConanFile):
    name = "re2c"
    description = "re2c is a free and open-source lexer generator for C/C++, Go and Rust."
    license = "LicenseRef-re2c"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://re2c.org/"
    topics = ("lexer", "language", "tokenizer", "flex")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
            self.tool_requires("winflexbison/2.5.24")
            if is_msvc(self):
                self.tool_requires("cccl/1.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--disable-benchmarks")
        env = tc.environment()
        if is_msvc(self):
            tc.extra_cxxflags.append("-EHsc")
            env.define("CC", "cccl -FS")
            env.define("CXX", "cccl -FS")
            env.define("LD", "cccl")
            env.define("CXXLD", "cccl")
        tc.generate(env)

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Don't copy benchmark files, which cause the build to fail on Windows
        replace_in_file(self, os.path.join(self.source_folder, "configure"),
                        '"$ac_config_files Makefile ',
                        '"$ac_config_files Makefile" #',
                        strict=False)
        replace_in_file(self, os.path.join(self.source_folder, "configure"),
                        '"$ac_config_links ',
                        '"$ac_config_links" #',
                        strict=False)

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make(args=["V=1"])

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"),
             keep_path=False)
        copy(self, "NO_WARRANTY",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"),
             keep_path=False)
        copy(self, "*.re",
             src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"),
             keep_path=False)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        include_dir = os.path.join(self.package_folder, "include")
        self.buildenv_info.define("RE2C_STDLIB_DIR", include_dir)

        # TODO: to remove in conan v2
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
        self.env_info.RE2C_STDLIB_DIR = include_dir
