
import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class Package7Zip(ConanFile):
    name = "7zip"
    version = "19.00"
    url = "https://github.com/conan-io/conan-center-index"
    description = "7-Zip is a file archiver with a high compression ratio"
    license = ("LGPL-2.1", "BSD-3-Clause", "Unrar")
    author = "Conan Community"
    homepage = "https://www.7-zip.org"
    topics = ("conan", "7zip", "zip", "compression", "decompression")
    settings = "os_build", "arch_build"

    def configure(self):
        if self.settings.os_build != "Windows":
            raise ConanInvalidConfiguration("Only Windows supported")

    def source(self):
        tools.download(**self.conan_data["sources"][self.version])
        tools.check_sha256(**self.conan_data["checksum"][self.version])
        self._uncompress_7z(self.conan_data["sources"][self.version]["filename"])

    def _uncompress_7z(self, filename):
        """ We need 7z itself to uncompress the file, we have two options:
            * download an executable and run it
            * booststrap using a previous version (7zip/9.22) where sources are in .tar.bz2. Right
              now it would we a loop in the Conan graph
        """
        tools.get(**self.conan_data["externals"]["lzma"])
        self.run("lzma920\\7zr.exe x {}".format(filename))

    def build(self):
        if self.settings.os_build == "Windows":
            env_build = VisualStudioBuildEnvironment(self)
            with tools.environment_append(env_build.vars):
                vcvars = tools.vcvars_command(self.settings)
                with tools.chdir("CPP/7zip"):
                    self.run("%s && nmake /f makefile" % vcvars)
        else:
            # TODO: Enable non-Windows methods in configure
            env_build = AutoToolsBuildEnvironment(self)
            with tools.environment_append(env_build.vars):
                with tools.chdir("CPP/7zip/Bundles/LzmaCon"):
                    self.run("make -f makefile.gcc all")

    def package(self):
        self.copy("DOC/License.txt", src="", dst="licenses")
        self.copy("DOC/unRarLicense.txt", src="", dst="licenses")
        if self.settings.os_build == "Windows":
            self.copy("*.exe", src="CPP/7zip", dst="bin", keep_path=False)
            self.copy("*.dll", src="CPP/7zip", dst="bin", keep_path=False)

        # TODO: Package the libraries: binaries and headers (add the rest of settings)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.path.append(bin_path)
