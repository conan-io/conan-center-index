from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.files import chdir, copy, get
from conan.tools.layout import basic_layout

from contextlib import contextmanager
import os

required_conan_version = ">=1.47.0"


class B2Conan(ConanFile):
    name = "b2"
    homepage = "https://www.bfgroup.xyz/b2/"
    description = "B2 makes it easy to build C++ projects, everywhere."
    topics = ("installer", "builder", "build", "build-system")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        'use_cxx_env': [False, True],
        'toolset': [
            'auto', 'cxx', 'cross-cxx',
            'acc', 'borland', 'clang', 'como', 'gcc-nocygwin', 'gcc',
            'intel-darwin', 'intel-linux', 'intel-win32', 'kcc', 'kylix',
            'mingw', 'mipspro', 'pathscale', 'pgi', 'qcc', 'sun', 'sunpro',
            'tru64cxx', 'vacpp', 'vc12', 'vc14', 'vc141', 'vc142', 'vc143',
        ]
    }
    default_options = {
        'use_cxx_env': False,
        'toolset': 'auto'
    }
    options_description = {
        'use_cxx_env': (
            "Indicates if the build will use the CXX and "
            "CXXFLAGS environment variables. The common use is to add additional flags "
            "for building on specific platforms or for additional optimization options."
        ),
        'toolset': (
            "Specifies the toolset to use for building. The default of 'auto' detects "
            "a usable compiler for building and should be preferred. The 'cxx' toolset "
            "uses the 'CXX' and 'CXXFLAGS' solely for building. Using the 'cxx' "
            "toolset will also turn on the 'use_cxx_env' option. And the 'cross-cxx' "
            "toolset uses the 'BUILD_CXX' and 'BUILD_CXXFLAGS' vars. This frees the "
            "'CXX' and 'CXXFLAGS' variables for use in subprocesses."
        ),
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type
        del self.info.options.use_cxx_env
        del self.info.options.toolset

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration(f"{self.ref} recipe doesn't support cross-build yet")

        if self.options.toolset in ['cxx', 'cross-cxx'] and not self.options.use_cxx_env:
            raise ConanInvalidConfiguration(
                "Option toolset 'cxx' and 'cross-cxx' requires 'use_cxx_env=True'")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _b2_dir(self):
        return self.source_folder

    @property
    def _b2_engine_dir(self):
        return os.path.join(self._b2_dir, "src", "engine")

    @property
    def _b2_output_dir(self):
        return os.path.join(self.build_folder, "output")

    @property
    def _pkg_bin_dir(self):
        return os.path.join(self.package_folder, "bin")

    @contextmanager
    def _bootstrap_env(self):
        saved_env = dict(os.environ)
        # Vcvars will change the directory after it runs in the situation when
        # the user has previously run the VS command console inits. In that
        # context it remembers the dir and resets it at each vcvars invocation.
        os.environ.update({"VSCMD_START_DIR": os.getcwd()})
        if not self.options.use_cxx_env:
            # To avoid using the CXX env vars we clear them out for the build.
            os.environ.update({
                "CXX": "",
                "CXXFLAGS": ""})
        try:
            yield
        finally:
            os.environ.clear()
            os.environ.update(saved_env)

    def build(self):
        self.output.info("Build engine..")
        use_windows_commands = os.name == "nt"
        command = "build" if use_windows_commands else "./build.sh"
        toolset_arg = ""
        if self.options.toolset != "auto":
            toolset_arg = str(self.options.toolset)
        with chdir(self, self._b2_engine_dir):
            with self._bootstrap_env():
                self.run(f"{command} {toolset_arg}")

        command = os.path.join(self._b2_engine_dir, "b2.exe" if use_windows_commands else "b2")
        toolset_arg = ""
        if self.options.toolset != "auto":
            toolset_arg = f"toolset={self.options.toolset}"
        with chdir(self, self.source_folder):
            self.run(
                f"{command} --ignore-site-config --prefix=../output --abbreviate-paths {toolset_arg} install"
            )

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*b2", dst=self._pkg_bin_dir, src=self._b2_output_dir)
        copy(self, "*b2.exe", dst=self._pkg_bin_dir, src=self._b2_output_dir)
        copy(self, "*.jam", dst=self._pkg_bin_dir, src=self._b2_output_dir)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2
        self.env_info.PATH.append(self._pkg_bin_dir)
