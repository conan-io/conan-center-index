import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class PackageApacheMaven(ConanFile):
    name = "maven"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Apache Maven is a software project management and comprehension tool"
    license = ("Apache-2.0")
    homepage = "https://maven.apache.org/"
    topics = ("conan", "maven", "java")
    settings = "os", "arch", "compiler"

    requires = ("zulu-openjdk/11.0.8")

    def configure(self):
        if self.settings.arch not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration("Unsupported architecture")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "apache-maven-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def package(self):
        self.copy("*", dst="", src=self._source_subfolder)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.cpp_info.bindirs.append(bin_path)
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

