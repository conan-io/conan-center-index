import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class SwigConan(ConanFile):
    name = "swig"
    description = "SWIG is a software development tool that connects programs written in C and C++ with a variety of high-level programming languages."
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.swig.org"
    topics = ("python", "java", "wrapper")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        copy(self, "cmake/*", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _use_pcre2(self):
        return Version(self.version) >= "4.1"

    def requirements(self):
        if self._use_pcre2:
            self.requires("pcre2/10.42")
        else:
            self.requires("pcre/8.45")

    def package_id(self):
        del self.info.settings.compiler

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
            if is_msvc(self):
                self.tool_requires("cccl/1.3")
        if is_msvc(self):
            self.tool_requires("winflexbison/2.5.24")
        else:
            self.tool_requires("bison/3.8.2")
        self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        if self.settings.os == "Windows" and not is_msvc(self):
            tc.extra_ldflags.append("-static")

        tc.configure_args += [
            f"--host={self.settings.arch}",
            "--with-swiglibdir=${prefix}/bin/swiglib",
        ]
        if self.settings.os in ["Linux", "FreeBSD"]:
            tc.configure_args.append("LIBS=-ldl")
        elif self.settings.os == "Windows" and not is_msvc(self):
            tc.configure_args.append("LIBS=-lmingwex -lssp")

        env = tc.environment()
        if is_msvc(self):
            env.define("CC", "cccl")
            env.define("CXX", "cccl")
            self.output.warning("Visual Studio compiler cannot create ccache-swig. Disabling ccache-swig.")
            tc.configure_args.append("--disable-ccache")
            tc.extra_cxxflags.append("-FS")

        if is_apple_os(self) and self.settings.arch == "armv8":
            # FIXME: Apple ARM should be handled by build helpers
            tc.extra_cxxflags.append("-arch arm64")
            tc.extra_ldflags.append("-arch arm64")

        tc.generate(env)

        tc = AutotoolsDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            self.run("./autogen.sh")
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "COPYRIGHT", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*.cmake", dst=self._module_subfolder, src=os.path.join(self.export_sources_folder, "cmake"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        for path in self.package_path.iterdir():
            if path.is_dir() and path.name not in ["bin", "lib", "licenses"]:
                rmdir(self, path)

    @property
    def _swiglibdir(self):
        return os.path.join(self.package_folder, "bin", "swiglib").replace("\\", "/")

    @property
    def _module_subfolder(self):
        return os.path.join(self.package_folder, "lib", "cmake")

    @property
    def _module_path(self):
        return os.path.join(self._module_subfolder, f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.set_property("cmake_file_name", "SWIG")
        self.cpp_info.set_property("cmake_target_name", "SWIG::SWIG")
        self.cpp_info.set_property("cmake_build_modules", [self._module_path])

        self.runenv.define_path("SWIG_LIB", os.path.join(self.package_folder, "bin", "swiglib"))
        self.buildenv.define_path("SWIG_LIB", os.path.join(self.package_folder, "bin", "swiglib"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "SWIG"
        self.cpp_info.names["cmake_find_package_multi"] = "SWIG"
        self.cpp_info.builddirs = [self._module_subfolder]
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_path]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)
        self.env_info.SWIG_LIB = os.path.join(self.package_folder, "bin", "swiglib")
