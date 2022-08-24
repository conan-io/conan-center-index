from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.tools.microsoft import is_msvc
from contextlib import contextmanager
import os
import shutil

required_conan_version = ">=1.45.0"


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac", "Makefile.am", "test_package_1.c", "test_package.cpp"
    # DON'T COPY extra.m4 TO BUILD FOLDER!!!
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    @contextmanager
    def _build_context(self):
        if is_msvc(self):
            with tools.vcvars(self):
                with tools.environment_append({"CC": "cl -nologo", "CXX": "cl -nologo",}):
                    yield
        else:
            yield

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
    
    @property
    def _user_info(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def _build_scripts(self):
        """Test compile script of automake"""
        compile_script = self._user_info["automake"].compile
        ar_script = self._user_info["automake"].ar_lib
        assert os.path.isfile(ar_script)
        assert os.path.isfile(compile_script)

        if self._system_cc:
            with tools.vcvars(self) if is_msvc(self) else tools.no_op():
                self.run("{} {} test_package_1.c -o script_test".format(tools.microsoft.unix_path(self, compile_script), self._system_cc), win_bash=tools.os_info.is_windows)

    def _build_autotools(self):
        """Test autoreconf + configure + make"""
        with tools.environment_append({"AUTOMAKE_CONAN_INCLUDES": [tools.microsoft.unix_path(self, self.source_folder)]}):
            self.run("{} -fiv".format(os.environ["AUTORECONF"]), win_bash=tools.os_info.is_windows)
        self.run("{} --help".format(os.path.join(self.build_folder, "configure").replace("\\", "/")), win_bash=tools.os_info.is_windows)
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools.configure()
            autotools.make()

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), self.build_folder)

        self._build_scripts()
        self._build_autotools()

    def test(self):
        if self._system_cc:
            if not tools.build.cross_building(self, self):
                self.run(os.path.join(".", "script_test"), run_environment=True)

        if not tools.build.cross_building(self, self):
            self.run(os.path.join(".", "test_package"), run_environment=True)
