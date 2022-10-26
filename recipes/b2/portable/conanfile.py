import os
from contextlib import contextmanager
import conan.tools.files
import conan.tools.layout
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.52.0"


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
        conan.tools.layout.basic_layout(self, src_folder="source")

    def source(self):
        conan.tools.files.get(
            self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def b2_dir(self):
        return os.path.join(self.source_folder)

    @property
    def b2_engine_dir(self):
        return os.path.join(self.b2_dir, "src", "engine")

    @property
    def b2_output_dir(self):
        return os.path.join(self.build_folder, "output")

    @property
    def pkg_licenses_dir(self):
        return os.path.join(self.package_folder, "licenses")

    @property
    def pkg_bin_dir(self):
        return os.path.join(self.package_folder, "bin")

    @contextmanager
    def bootstrap_env(self):
        saved_env = dict(os.environ)
        os.environ.update({"VSCMD_START_DIR": self.b2_dir})
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
        use_windows_commands = os.name == 'nt'
        command = "build" if use_windows_commands else "./build.sh"
        if self.options.toolset != 'auto':
            command += " "+str(self.options.toolset)
        with conan.tools.files.chdir(self, self.b2_engine_dir):
            with self.bootstrap_env():
                self.run(command)

        self.output.info("Install..")
        command = os.path.join(
            self.b2_engine_dir, "b2.exe" if use_windows_commands else "b2")
        # auto, cxx, and cross-cxx aren't toolsets in b2; they're only used to affect
        # the way build.sh builds b2. Don't pass them to b2 itself.
        if self.options.toolset not in ['auto', 'cxx', 'cross-cxx']:
            command += " toolset=" + str(self.options.toolset)
        full_command = \
            ("{0} --ignore-site-config " +
             "--prefix={1} " +
             "--abbreviate-paths " +
             "install " +
             "b2-install-layout=portable").format(command, self.b2_output_dir)
        with conan.tools.files.chdir(self, self.b2_dir):
            self.run(full_command)

    def package(self):
        conan.tools.files.copy(
            self, "LICENSE.txt", dst=self.pkg_licenses_dir, src=self.source_folder)
        conan.tools.files.copy(
            self, "*b2", dst=self.pkg_bin_dir, src=self.b2_output_dir)
        conan.tools.files.copy(
            self, "*b2.exe", dst=self.pkg_bin_dir, src=self.b2_output_dir)
        conan.tools.files.copy(
            self, "*.jam", dst=self.pkg_bin_dir, src=self.b2_output_dir)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = ["bin"]
        self.buildenv_info.prepend_path("PATH", self.pkg_bin_dir)

    def package_id(self):
        del self.info.options.use_cxx_env
        del self.info.options.toolset
