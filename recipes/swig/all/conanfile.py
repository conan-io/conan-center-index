from conan import ConanFile, tools
from conan.tools.files import get, copy, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.env import VirtualBuildEnv
from conan.tools.microsoft import is_msvc
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.55.0"


class SwigConan(ConanFile):
    name = "swig"
    description = "SWIG is a software development tool that connects programs written in C and C++ with a variety of high-level programming languages."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.swig.org"
    license = "GPL-3.0-or-later"
    topics = ("swig", "python", "java", "wrapper")
    exports_sources = "patches/**", "cmake/*"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _use_pcre2(self):
        return self.version not in ['4.0.1', '4.0.2']


    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self._use_pcre2:
            self.requires("pcre2/10.40")
        else:
            self.requires("pcre/8.45")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "msvc":
            self.build_requires("winflexbison/2.5.24")
        else:
            self.build_requires("bison/3.8.2")
        self.build_requires("automake/1.16.5")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)

        if self.settings.os == "Linux":
            tc.extra_ldflags.append("-ldl")
        if self.settings.os == "Windows" and self.settings.compiler != "msvc":
            tc.extra_ldflags.append("-static")
        if is_msvc(self):
            tc.configure_args.append('--disable-ccache')

        deps = AutotoolsDeps(self)
        deps.generate()

        tc.configure_args.extend([
            "--host={}".format(self.settings.arch),
            "--with-swiglibdir={}".format(os.path.join("bin", "swiglib")),
        ])

        env = tc.environment()
        if is_msvc(self):
            tc.extra_cflags.append("-FS")
            env.define("CC", "{} cl -nologo")
            env.define("CXX", "{} cl -nologo")
            env.define("AR", f"{ar_wrapper} lib")
            env.define("LD", "link")
        tc.generate(env)

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        self.run("./autogen.sh", cwd=self.source_folder)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self._source_subfolder)
        copy(self, pattern="COPYRIGHT", dst=os.path.join(self.package_folder, "licenses"), src=self._source_subfolder)
        copy(self, "*", src="cmake", dst=self._module_subfolder)
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    @property
    def _swiglibdir(self):
        return os.path.join(self.package_folder, "bin", "swiglib").replace("\\", "/")

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return "conan-official-{}-targets.cmake".format(self.name)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.builddirs = [self._module_subfolder]
        self.cpp_info.set_property("cmake_build_modules", [
            os.path.join(self._module_subfolder, self._module_file)
        ])
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.buildenv_info.append_path("PATH", os.path.join(self.package_folder, bindir))
