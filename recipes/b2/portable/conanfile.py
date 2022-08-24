from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


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

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination="source")

    def build(self):
        use_windows_commands = os.name == 'nt'
        command = "build" if use_windows_commands else "./build.sh"
        if self.options.toolset != 'auto':
            command += " "+str(self.options.toolset)
        build_dir = os.path.join(self.source_folder, "source")
        engine_dir = os.path.join(build_dir, "src", "engine")
        os.chdir(engine_dir)
        with tools.environment_append({"VSCMD_START_DIR": os.curdir}):
            if self.options.use_cxx_env:
                # Allow use of CXX env vars.
                self.run(command)
            else:
                # To avoid using the CXX env vars we clear them out for the build.
                with tools.environment_append({"CXX": "", "CXXFLAGS": ""}):
                    self.run(command)
        os.chdir(build_dir)
        command = os.path.join(
            engine_dir, "b2.exe" if use_windows_commands else "b2")
        # auto, cxx, and cross-cxx aren't toolsets in b2; they're only used to affect
        # the way build.sh builds b2. Don't pass them to b2 itself.
        if self.options.toolset not in ['auto', 'cxx', 'cross-cxx']:
            command += " toolset=" + str(self.options.toolset)
        full_command = \
            "{0} --ignore-site-config --prefix=../output --abbreviate-paths install b2-install-layout=portable".format(
                command)
        self.run(full_command)

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src="source")
        self.copy(pattern="*b2", dst="bin", src="output")
        self.copy(pattern="*b2.exe", dst="bin", src="output")
        self.copy(pattern="*.jam", dst="bin", src="output")

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.bindirs = ["bin"]
        self.env_info.path = [os.path.join(
            self.package_folder, "bin")]

    def package_id(self):
        del self.info.options.use_cxx_env
        del self.info.options.toolset
