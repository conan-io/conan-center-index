
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
    settings = "os_build", "arch_build", "compiler"

    def build_requirements(self):
        if tools.os_info.is_windows and os.environ.get("CONAN_BASH_PATH", None) is None:
            if self.settings.compiler != "Visual Studio":
                self.build_requires("msys2/20161025")

    def configure(self):
        if self.settings.os_build != "Windows":
            raise ConanInvalidConfiguration("Only Windows supported")
        if self.settings.arch_build not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration("Unsupported architecture")

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

    _msvc_platforms = {
        'x86_64': 'x64',
        'x86': 'x86',
    }

    def _build_msvc(self):
        env_build = VisualStudioBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            vcvars = tools.vcvars_command(self.settings)
            with tools.chdir("CPP/7zip"):
                self.run("%s && nmake /f makefile PLATFORM=%s" % (
                vcvars, self._msvc_platforms[str(self.settings.arch_build)]))

    def _build_autotools(self):
        # TODO: Enable non-Windows methods in configure
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            with tools.chdir("CPP/7zip/Bundles/LzmaCon"):
                self.run("make -f makefile.gcc all")

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        self.copy("DOC/License.txt", src="", dst="licenses")
        self.copy("DOC/unRarLicense.txt", src="", dst="licenses")
        if self.settings.os_build == "Windows":
            self.copy("*.exe", src="CPP/7zip", dst="bin", keep_path=False)
            self.copy("*.dll", src="CPP/7zip", dst="bin", keep_path=False)

        # TODO: Package the libraries: binaries and headers (add the rest of settings)

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.path.append(bin_path)
