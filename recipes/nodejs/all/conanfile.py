import os
import re
from conans import __version__
from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.files import copy, get
from conan.errors import ConanInvalidConfiguration

from six import StringIO

required_conan_version = ">=1.59.0"


class NodejsConan(ConanFile):
    name = "nodejs"
    description = "nodejs binaries for use in recipes"
    topics = ("node", "nodejs")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nodejs.org"
    license = "MIT"
    settings = "os", "arch", "compiler"
    no_copy_source = True
    short_paths = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    @property
    def _nodejs_arch(self):
        if str(self.info.settings.os) == "Linux":
            if str(self.info.settings.arch).startswith("armv7"):
                return "armv7"
            if str(self.info.settings.arch).startswith("armv8") and "32" not in str(self.info.settings.arch):
                return "armv8"
        return str(self.info.settings.arch)

    @property
    def _glibc_version(self):
        buff = StringIO()
        self.run(['ldd', '--version'], output=buff)
        buff = re.search('GLIBC \d{1,3}.\d{1,3}', buff.getvalue())
        return str(buff.group()[6:])

    def validate(self):
        if not self.version in self.conan_data["sources"] or \
           not str(self.info.settings.os) in self.conan_data["sources"][self.version] or \
           not self._nodejs_arch in self.conan_data["sources"][self.version][str(self.info.settings.os)]:
            raise ConanInvalidConfiguration("Binaries for this combination of architecture/version/os not available")

        if Version(self.version) >= "18.0.0":
            if str(self.info.settings.compiler) == "gcc" and Version(self.info.settings.compiler.version) < "8.3":
                raise ConanInvalidConfiguration("Binaries for this combination of architecture/version/os not available")

            if str(self.info.settings.os) == "Linux":
                if Version(self._glibc_version) < '2.27':
                    raise ConanInvalidConfiguration("Binaries for this combination of architecture/version/os not available")

    def build(self):
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version][str(self.info.settings.os)][self._nodejs_arch], destination=self._source_subfolder, strip_root=True)

    def package(self):
        if Version(__version__) < '2.0.0':
            self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
            self.copy(pattern="*", src=os.path.join(self._source_subfolder, "bin"), dst="bin")
            self.copy(pattern="*", src=os.path.join(self._source_subfolder, "lib"), dst="lib")
            self.copy(pattern="node.exe", src=self._source_subfolder, dst="bin")
            self.copy(pattern="npm", src=self._source_subfolder, dst="bin")
            self.copy(pattern="npx", src=self._source_subfolder, dst="bin")
        else:
            copy(self, pattern="LICENSE", dst="licenses", src=self._source_subfolder)
            copy(self, pattern="*", src=os.path.join(self._source_subfolder, "bin"), dst="bin")
            copy(self, pattern="*", src=os.path.join(self._source_subfolder, "lib"), dst="lib")
            copy(self, pattern="node.exe", src=self._source_subfolder, dst="bin")
            copy(self, pattern="npm", src=self._source_subfolder, dst="bin")
            copy(self, pattern="npx", src=self._source_subfolder, dst="bin")

    def package_info(self):
        self.cpp_info.includedirs = []
        bin_dir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bin_dir))
        self.env_info.PATH.append(bin_dir)
