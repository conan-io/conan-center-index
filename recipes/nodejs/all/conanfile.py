import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class NodejsConan(ConanFile):
    name = "nodejs"
    description = "nodejs binaries for use in recipes"
    topics = ("conan", "node", "nodejs")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nodejs.org"
    license = "MIT"
    settings = "os", "arch"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    @property
    def _nodejs_arch(self):
        if str(self.settings.os) == "Linux":
            if str(self.settings.arch).startswith("armv7"):
                return "armv7"
            if str(self.settings.arch).startswith("armv8") and "32" not in str(self.settings.arch):
                return "armv8"
        return str(self.settings.arch)

    def validate(self):
        if (not (self.version in self.conan_data["sources"]) or
            not (str(self.settings.os) in self.conan_data["sources"][self.version]) or
            not (self._nodejs_arch in self.conan_data["sources"][self.version][str(self.settings.os)] ) ):
            raise ConanInvalidConfiguration("Binaries for this combination of architecture/version/os not available")

    def build(self):
        tools.files.get(self, **self.conan_data["sources"][self.version][str(self.settings.os)][self._nodejs_arch], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", src=os.path.join(self._source_subfolder, "bin"), dst="bin")
        self.copy(pattern="node.exe", src=self._source_subfolder, dst="bin")
        self.copy(pattern="npm", src=self._source_subfolder, dst="bin")
        self.copy(pattern="npx", src=self._source_subfolder, dst="bin")

    def package_info(self):
        self.cpp_info.includedirs = []
        bin_dir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bin_dir))
        self.env_info.PATH.append(bin_dir)
