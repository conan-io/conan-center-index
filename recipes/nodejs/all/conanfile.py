import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class NodejsInstallerConan(ConanFile):
    name = "nodejs"
    description = "nodejs binaries for use in recipes"
    topics = ("conan", "node", "nodejs")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nodejs.org"
    license = "MIT"
    settings = "os_build", "arch_build"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def configure(self):
        if self.settings.arch_build == "x86" and self.settings.os_build == "Linux":
            raise ConanInvalidConfiguration("Linux x86 is not support by nodejs")
        if self.settings.os_build not in ["Windows", "Macos", "Windows"]:
            raise ConanInvalidConfiguration("The OS '%s' is not support by nodejs" % str(self.settings.os_build))

    def source(self):
        for data in self.conan_data["sources"][self.version]:
            oss, sha, url = data.values()
            filename = url[url.rfind("/")+1:]
            tools.download(url, filename)
            tools.check_sha256(filename, sha)
            if self.settings.os_build == oss:
                tools.unzip(filename)
                os.rename(filename[:filename.rfind(".")], self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="node", src=self._source_subfolder, dst="bin")
        self.copy(pattern="node.exe", src=self._source_subfolder, dst="bin")
        self.copy(pattern="npm", src=self._source_subfolder, dst="bin")
        self.copy(pattern="npx", src=self._source_subfolder, dst="bin")

    def package_info(self):
        bin_dir = self.package_folder if tools.os_info.is_windows else os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bin_dir))
        self.env_info.PATH.append(bin_dir)
