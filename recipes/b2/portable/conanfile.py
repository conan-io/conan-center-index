import os
import shutil

from conan import ConanFile
from conan.tools.build import can_run, check_min_cppstd
from conan.tools.env import VirtualBuildEnv, Environment
from conan.tools.files import copy, get, save, load, replace_in_file
from conan.tools.gnu import AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import VCVars, is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.0"


class B2Conan(ConanFile):
    name = "b2"
    homepage = "https://www.bfgroup.xyz/b2/"
    description = "B2 makes it easy to build C++ projects, everywhere."
    topics = ("installer", "builder", "build", "build-system")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    package_type = "application"
    options = {
        "build_grammar": [True, False],
        "use_cxx_env": ["deprecated", False, True],
        "toolset": [
            "deprecated",
            "auto", "cxx", "cross-cxx",
            "acc", "borland", "clang", "como", "gcc-nocygwin", "gcc",
            "intel-darwin", "intel-linux", "intel-win32", "kcc", "kylix",
            "mingw", "mipspro", "pathscale", "pgi", "qcc", "sun", "sunpro",
            "tru64cxx", "vacpp", "vc12", "vc14", "vc141", "vc142", "vc143",
        ]
    }
    default_options = {
        "build_grammar": False,
        "use_cxx_env": "deprecated",
        "toolset": "deprecated",
    }

    def _is_macos_intel_or_arm(self, settings):
        return settings.os == "Macos" and settings.arch in ["x86_64", "armv8"]

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler
        if self._is_macos_intel_or_arm(self.info.settings):
            self.info.settings.arch = "x86_64,armv8"

    def validate_build(self):
        check_min_cppstd(self, 11)

    def requirements(self):
        if Version(self.version) >= "5.2.0":
            self.requires("nlohmann_json/[^3]")

    def validate(self):
        if self.options.use_cxx_env.value != "deprecated":
            self.output.warn("The 'use_cxx_env' option is deprecated and will be removed in a future version.")
        if self.options.toolset.value != "deprecated":
            self.output.warn("The 'toolset' option is deprecated and will be removed in a future version.")

    def build_requirements(self):
        if not can_run(self):
            self.tool_requires(f"b2/{self.version}")
        if self.options.build_grammar:
            if self.settings_build.os == "Windows":
                self.tool_requires("winflexbison/2.5.25")
            else:
                self.tool_requires("bison/3.8.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Ensure CXXFLAGS are respected
        replace_in_file(self, os.path.join("src", "engine", "config_toolset.bat"),
                        '"B2_CXX="%CXX%" ',
                        '"B2_CXX="%CXX%" %CXXFLAGS% ')
        if Version(self.version) >= "5.2.0":
            os.unlink(os.path.join("src", "engine", "ext_nlohmann_json.hpp"))
            replace_in_file(self, os.path.join("src", "engine", "mod_db.cpp"),
                            '#include "ext_nlohmann_json.hpp"',
                            "#include <nlohmann/json.hpp>")

    @property
    def _toolchain_vars(self):
        return AutotoolsToolchain(self).environment().vars(self)

    @property
    def _cxx(self):
        if is_msvc(self):
            return "cl"
        cxx = self._toolchain_vars.get("CXX")
        if cxx:
            return cxx
        compiler_version = Version(self.settings.compiler.version)
        major = compiler_version.major
        compiler = str(self.settings.compiler)
        compiler = {"gcc": "g++", "clang": "clang++"}.get(compiler, compiler)
        return shutil.which(f"{compiler}-{compiler_version}") or shutil.which(f"{compiler}-{major}") or compiler

    @property
    def _cxxflags(self):
        cxxflags = self._toolchain_vars.get("CXXFLAGS", "")
        cxxflags += " " + VirtualBuildEnv(self).vars().get("CXXFLAGS", default="")
        if self._is_macos_intel_or_arm(self.settings):
            cxxflags += " -arch arm64 -arch x86_64"
        if Version(self.version) >= "5.2.0":
            json_incdir = self.dependencies["nlohmann_json"].cpp_info.includedir
            cxxflags += f" -I{json_incdir}"
        return cxxflags.strip()

    @property
    def _windows_toolset(self):
        # msvc, borland, como, gcc, clang, clang-win, gcc-nocygwin, intel-win32, mingw
        if self.settings.compiler == "clang" and self.settings.compiler.get_safe("runtime"):
            return "clang-win"
        return {
            "msvc": "msvc",
            "gcc": "mingw",
            "clang": "clang",
            "intel-cc": "intel-win32",
        # Use "clang" as the fall-back since it has the most generic build flags
        }.get(str(self.settings.compiler), "clang")

    def generate(self):
        VirtualBuildEnv(self).generate()
        build_args = []
        if self.settings_build.os == "Windows":
            if is_msvc(self):
                VCVars(self).generate()
            env = Environment()
            env.define("CXX", self._cxx)
            env.define("CXXFLAGS", self._cxxflags)
            env.define("BISON", "win_bison")
            env.vars(self).save_script("b2_vars")
            build_args.append(self._windows_toolset)
        else:
            build_args.append(f"--cxx={self._cxx}")
            cxxflags = self._cxxflags
            if cxxflags:
                build_args.append(f'--cxxflags="{cxxflags}"')
            if self.settings.build_type in ["Debug", "RelWithDebInfo"]:
                build_args.append("--debug")
        save(self, "build_args", " ".join(build_args))

    @property
    def _b2_engine_dir(self):
        return os.path.join(self.source_folder, "src", "engine")

    def build(self):
        command = "build.bat" if self.settings_build.os == "Windows" else "./build.sh"
        args = load(self, os.path.join(self.generators_folder, "build_args"))
        self.run(f"{command} {args}", cwd=self._b2_engine_dir)

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        b2 = os.path.join(self._b2_engine_dir, "b2") if can_run(self) else "b2"
        self.run(" ".join([
            b2,
            "install",
            "b2-install-layout=portable",
            "--ignore-site-config",
            "--abbreviate-paths",
            f"--prefix={os.path.join(self.package_folder, 'bin')}",
        ]), cwd=self.source_folder)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
