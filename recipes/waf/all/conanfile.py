from conan import ConanFile, tools
import os


class WafConan(ConanFile):
    name = "waf"
    description = "The Waf build system"
    topics = ("conan", "waf", "builsystem")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://waf.io"
    license = "BSD-3-Clause"
    settings = "os", "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("waf-{}".format(self.version), self._source_subfolder)

    @property
    def _license_text(self):
        [_, license, _] = open(os.path.join(self.source_folder, self._source_subfolder, "waf"), "rb").read().split(b"\"\"\"", 3)
        return license.decode().lstrip()

    def build(self):
        pass

    def package(self):
        binpath = os.path.join(self.package_folder, "bin")
        libpath = os.path.join(self.package_folder, "lib")

        os.mkdir(binpath)
        os.mkdir(libpath)

        tools.files.save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._license_text)

        self.copy("waf", src=self._source_subfolder, dst=binpath)
        self.copy("waf-light", src=self._source_subfolder, dst=binpath)
        self.copy("waflib/*", src=self._source_subfolder, dst=libpath)

        if self.settings.os == "Windows":
            self.copy("waf.bat", src=os.path.join(self._source_subfolder, "utils"), dst=binpath)

        os.chmod(os.path.join(binpath, "waf"), 0o755)
        os.chmod(os.path.join(binpath, "waf-light"), 0o755)

    def package_info(self):
        self.cpp_info.libdirs = []

        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var: {}".format(binpath))
        self.env_info.PATH.append(binpath)

        wafdir = os.path.join(self.package_folder, "lib")
        self.output.info("Setting WAFDIR env var: {}".format(wafdir))
        self.env_info.WAFDIR = wafdir


