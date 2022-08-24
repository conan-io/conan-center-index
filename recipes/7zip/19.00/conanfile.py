from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class SevenZipConan(ConanFile):
    name = "7zip"
    url = "https://github.com/conan-io/conan-center-index"
    description = "7-Zip is a file archiver with a high compression ratio"
    license = ("LGPL-2.1", "BSD-3-Clause", "Unrar")
    homepage = "https://www.7-zip.org"
    topics = ("7zip", "zip", "compression", "decompression")
    settings = "os", "arch", "compiler"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Only Windows supported")
        if self.settings.arch not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration("Unsupported architecture")

    def build_requirements(self):
        self.build_requires("lzma_sdk/9.20")

        if self.settings.compiler != "Visual Studio" and self._settings_build.os == "Windows" and "make" not in os.environ.get("CONAN_MAKE_PROGRAM", ""):
            self.build_requires("make/4.2.1")

    def package_id(self):
        del self.info.settings.compiler

    def _uncompress_7z(self, filename):
        self.run("7zr x {}".format(filename))

    def source(self):
        from six.moves.urllib.parse import urlparse
        url = self.conan_data["sources"][self.version]["url"]
        filename = os.path.basename(urlparse(url).path)
        sha256 = self.conan_data["sources"][self.version]["sha256"]
        tools.files.download(self, url, filename)
        tools.check_sha256(filename, sha256)
        self._uncompress_7z(filename)
        os.unlink(filename)

    @property
    def _msvc_platform(self):
        return {
            "x86_64": "x64",
            "x86": "x86",
        }[str(self.settings.arch)]

    def _build_msvc(self):
        with tools.vcvars(self.settings):
            with tools.files.chdir(self, os.path.join("CPP", "7zip")):
                self.run("nmake /f makefile PLATFORM=%s" % self._msvc_platform)

    def _build_autotools(self):
        # TODO: Enable non-Windows methods in configure
        autotools = AutoToolsBuildEnvironment(self)
        extra_env = {}
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            extra_env["IS_MINGW"] = "1"
        with tools.environment_append(extra_env):
            with tools.files.chdir(self, os.path.join("CPP", "7zip", "Bundles", "LzmaCon")):
                autotools.make(args=["-f", "makefile.gcc"], target="all")

    def _patch_sources(self):
        if self.settings.compiler == "Visual Studio":
            fn = os.path.join("CPP", "Build.mak")
            os.chmod(fn, 0o644)
            tools.files.replace_in_file(self, fn, "-MT", "-{}".format(str(self.settings.compiler.runtime)))
            tools.files.replace_in_file(self, fn, "-MD", "-{}".format(str(self.settings.compiler.runtime)))

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        self.copy("DOC/License.txt", src="", dst="licenses")
        self.copy("DOC/unRarLicense.txt", src="", dst="licenses")
        if self.settings.os == "Windows":
            self.copy("*.exe", src="CPP/7zip", dst="bin", keep_path=False)
            self.copy("*.dll", src="CPP/7zip", dst="bin", keep_path=False)

        # TODO: Package the libraries: binaries and headers (add the rest of settings)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.path.append(bin_path)
