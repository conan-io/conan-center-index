import os
from contextlib import contextmanager
import conan.tools.files
import conan.tools.layout
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from six import StringIO

required_conan_version = ">=1.47.0"


class B2Conan(ConanFile):
    name = "b2"
    homepage = "https://www.bfgroup.xyz/b2/"
    description = "B2 makes it easy to build C++ projects, everywhere."
    topics = ("b2", "installer", "builder", "build", "build-system")
    license = "BSL-1.0"
    settings = "os", "arch"
    url = "https://github.com/conan-io/conan-center-index"

    '''
    * use_cxx_env: False, True

    Indicates if the build will use the CXX and
    CXXFLAGS environment variables. The common use is to add additional flags
    for building on specific platforms or for additional optimization options.

    * toolset: 'auto', 'cxx', 'cross-cxx',
    'acc', 'borland', 'clang', 'como', 'gcc-nocygwin', 'gcc',
    'intel-darwin', 'intel-linux', 'intel-win32', 'kcc', 'kylix',
    'mingw', 'mipspro', 'pathscale', 'pgi', 'qcc', 'sun', 'sunpro',
    'tru64cxx', 'vacpp', 'vc12', 'vc14', 'vc141', 'vc142', 'vc143'

    Specifies the toolset to use for building. The default of 'auto' detects
    a usable compiler for building and should be preferred. The 'cxx' toolset
    uses the 'CXX' and 'CXXFLAGS' solely for building. Using the 'cxx'
    toolset will also turn on the 'use_cxx_env' option. And the 'cross-cxx'
    toolset uses the 'BUILD_CXX' and 'BUILD_CXXFLAGS' vars. This frees the
    'CXX' and 'CXXFLAGS' variables for use in subprocesses.
    '''
    options = {
        'use_cxx_env': [False, True],
        'toolset': [
            'auto', 'cxx', 'cross-cxx',
            'acc', 'borland', 'clang', 'como', 'gcc-nocygwin', 'gcc',
            'intel-darwin', 'intel-linux', 'intel-win32', 'kcc', 'kylix',
            'mingw', 'mipspro', 'pathscale', 'pgi', 'qcc', 'sun', 'sunpro',
            'tru64cxx', 'vacpp', 'vc12', 'vc14', 'vc141', 'vc142', 'vc143']
    }
    default_options = {
        'use_cxx_env': False,
        'toolset': 'auto'
    }

    def validate(self):
        if (self.options.toolset == 'cxx' or self.options.toolset == 'cross-cxx') and not self.options.use_cxx_env:
            raise ConanInvalidConfiguration(
                "Option toolset 'cxx' and 'cross-cxx' requires 'use_cxx_env=True'")

    def layout(self):
        conan.tools.layout.basic_layout(self, src_folder="root")

    def source(self):
        conan.tools.files.get(
            self, **self.conan_data["sources"][self.version], strip_root=True)

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
    def _pkg_licenses_dir(self):
        return os.path.join(self.package_folder, "licenses")

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
        # The order of the with:with: below is important. The first one changes
        # the current dir. While the second does env changes that guarantees
        # that dir doesn't change if/when vsvars runs to set the msvc compile
        # env.
        self.output.info("Build engine..")
        command = ""
        b2_toolset = self.options.toolset
        use_windows_commands = os.name == 'nt'
        if b2_toolset == 'auto':
            if use_windows_commands:
                # For windows auto detection it can evaluate to a msvc version
                # that it's not aware of. Most likely because it's a future one
                # that didn't exist when the build was written. This turns that
                # into a generic msvc toolset build assuming it could work,
                # since it's a better version.
                with conan.tools.files.chdir(self, self._b2_engine_dir):
                    with self._bootstrap_env():
                        buf = StringIO()
                        self.run('guess_toolset && set', output=buf)
                        guess_vars = map(
                            lambda x: x.strip(), buf.getvalue().split("\n"))
                        if "B2_TOOLSET=vcunk" in guess_vars:
                            b2_toolset = 'msvc'
                            for kv in guess_vars:
                                if kv.startswith("B2_TOOLSET_ROOT="):
                                    b2_vcvars = os.path.join(
                                        kv.split('=')[1].strip(), 'Auxiliary', 'Build', 'vcvars32.bat')
                                    command += '"'+b2_vcvars+'" && '
        command += "build" if use_windows_commands else "./build.sh"
        if b2_toolset != 'auto':
            command += " "+str(b2_toolset)
        with conan.tools.files.chdir(self, self._b2_engine_dir):
            with self._bootstrap_env():
                self.run(command)

        self.output.info("Install..")
        command = os.path.join(
            self._b2_engine_dir, "b2.exe" if use_windows_commands else "b2")
        if b2_toolset not in ["auto", "cxx", "cross-cxx"]:
            command += " toolset=" + str(b2_toolset)
        full_command = \
            ("{0} --ignore-site-config " +
             "--prefix={1} " +
             "--abbreviate-paths " +
             "install " +
             "b2-install-layout=portable").format(command, self._b2_output_dir)
        with conan.tools.files.chdir(self, self._b2_dir):
            self.run(full_command)

    def package(self):
        conan.tools.files.copy(
            self, "LICENSE.txt", dst=self._pkg_licenses_dir, src=self.source_folder)
        conan.tools.files.copy(
            self, "*b2", dst=self._pkg_bin_dir, src=self._b2_output_dir)
        conan.tools.files.copy(
            self, "*b2.exe", dst=self._pkg_bin_dir, src=self._b2_output_dir)
        conan.tools.files.copy(
            self, "*.jam", dst=self._pkg_bin_dir, src=self._b2_output_dir)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = ["bin"]
        self.buildenv_info.prepend_path("PATH", self._pkg_bin_dir)
        self.env_info.path = [self._pkg_bin_dir]

    def package_id(self):
        del self.info.options.use_cxx_env
        del self.info.options.toolset
