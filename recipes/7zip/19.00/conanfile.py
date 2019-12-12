
import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class Package7Zip(ConanFile):
    name = "7zip"
    version = "19.00"
    url = "https://github.com/conan-io/conan-center-index"
    description = "7-Zip is a file archiver with a high compression ratio"
    license = ("LGPL-2.1", "BSD-3-Clause", "Unrar")
    homepage = "https://www.7-zip.org"
    topics = ("conan", "7zip", "zip", "compression", "decompression")
    settings = "os_build", "arch_build", "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.os_build != "Windows":
            raise ConanInvalidConfiguration("Only Windows supported")
        if self.settings.arch_build not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration("Unsupported architecture")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        commit = url[url.rfind("/")+1:url.rfind(".")]
        extracted_folder = "7z-" + commit
        os.rename(extracted_folder, self._source_subfolder)

    _msvc_platforms = {
        'x86_64': 'x64',
        'x86': 'x86',
    }

    def _build_msvc(self):
        env_build = VisualStudioBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            vcvars = tools.vcvars_command(self.settings)
            with tools.chdir(os.path.join(self._source_subfolder, "CPP", "7zip")):
                self.run("%s && nmake /f makefile PLATFORM=%s" % (
                vcvars, self._msvc_platforms[str(self.settings.arch_build)]))

    def _build_autotools(self):
        # TODO: Enable non-Windows methods in configure
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            with tools.chdir(os.path.join(self._source_subfolder, "CPP", "7zip", "Bundles", "LzmaCon")):
                self.run("make -f makefile.gcc all")

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        self.copy("License.txt", src=os.path.join(self._source_subfolder, "DOC"), dst="licenses")
        self.copy("unRarLicense.txt", src=os.path.join(self._source_subfolder, "DOC"), dst="licenses")
        if self.settings.os_build == "Windows":
            self.copy("*.exe", src=os.path.join(self._source_subfolder, "CPP", "7zip"), dst="bin", keep_path=False)
            self.copy("*.dll", src=os.path.join(self._source_subfolder, "CPP", "7zip"), dst="bin", keep_path=False)

        # TODO: Package the libraries: binaries and headers (add the rest of settings)

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.path.append(bin_path)
