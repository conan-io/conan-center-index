from conan import ConanFile

from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import copy, chdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

import os

required_conan_version = ">=1.45.0"


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac", "Makefile.am", "test_package_1.c", "test_package.cpp"
    # DON'T COPY extra.m4 TO BUILD FOLDER!!!
    test_type = "explicit"
    win_bash = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            self.build_requires("msys2/cci.latest")

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        env = Environment()

        if is_msvc(self):
            env.define("CC", "cl -nologo")
            env.define("CXX", "cl -nologo")
        
        compile_script = unix_path(self, self.dependencies["automake"].conf_info.get("user.automake:compile-wrapper"))

        env.define("COMPILE",compile_script )
        env.define("ACLOCAL_PATH", unix_path(self, os.path.join(self.source_folder)))
        env.vars(self, scope="build").save_script("automake_build_test")


    _default_cc = {
        "gcc": "gcc",
        "clang": "clang",
        "Visual Studio": "cl -nologo",
        "apple-clang": "clang",
    }

    @property
    def _system_cc(self):
        system_cc = os.environ.get("CC", None)
        if not system_cc:
            system_cc = self._default_cc.get(str(self.settings.compiler))
        return system_cc
    
    # def _build_scripts(self):


    #     if self._system_cc:
    #         with tools.vcvars(self) if is_msvc(self) else tools.no_op():
    #             self.run("{} {} test_package_1.c -o script_test".format(tools.unix_path(compile_script), self._system_cc), win_bash=tools.os_info.is_windows)

    # def _build_autotools(self):
    #     """Test autoreconf + configure + make"""
    #     with tools.environment_append({"AUTOMAKE_CONAN_INCLUDES": [tools.unix_path(self.source_folder)]}):
    #         self.run("{} -fiv".format(os.environ["AUTORECONF"]), win_bash=tools.os_info.is_windows)
    #     self.run("{} --help".format(os.path.join(self.build_folder, "configure").replace("\\", "/")), win_bash=tools.os_info.is_windows)
    #     autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
    #     with self._build_context():
    #         autotools.configure()
    #         autotools.make()

    def build(self):
        #Copy files to build folder
        for item in self.exports_sources:
            copy(self, item, self.source_folder, self.build_folder)
        # Test the compile wrapper for cl
        compiler_name = self._system_cc
        self.output.warning(f"source folder: {self.source_folder}")
        self.run("pwd")
        self.run("echo $COMPILE")
        self.run(f"$COMPILE {compiler_name} {self.source_folder}/test_package_1.c -o {self.build_folder}/script_test")
        

        # # Build test project
        with chdir(self, self.build_folder):
            self.run("autoreconf -fiv")
            self.run("./configure --help")
            self.run("./configure")
            self.run("make")
        # self.run("autoreconf ")
        # autotools = Autotools(self)
        # self.run("which autoreconf")
        # autotools.autoreconf()
        # self.run(f"{self.source_folder}/configure --help")
        # autotools.configure()
        # autotools.make()

    def test(self):
        self.run(f"{self.build_folder}/script_test")
        self.run(f"{self.build_folder}/test_package")
        pass
        # if self._system_cc:
        #     if not tools.cross_building(self):
        #         self.run(os.path.join(".", "script_test"), run_environment=True)

        # if not tools.cross_building(self):
        #     self.run(os.path.join(".", "test_package"), run_environment=True)
