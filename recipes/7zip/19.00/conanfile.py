import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
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

    def configure(self):
        if self.settings.os_build != "Windows":
            raise ConanInvalidConfiguration("Only Windows supported")
        if self.settings.arch_build not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration("Unsupported architecture")

    def source(self):
        from six.moves.urllib.parse import urlparse
        url = self.conan_data["sources"][self.version]["url"]
        filename = os.path.basename(urlparse(url).path)
        sha256 = self.conan_data["sources"][self.version]["sha256"]
        tools.download(url, filename)
        tools.check_sha256(filename, sha256)
        self._uncompress_7z(filename)
        os.unlink(filename)

    def build_requirements(self):
        self.build_requires("lzma_sdk/9.20")

        if tools.os_info.is_windows and "make" not in os.environ.get("CONAN_MAKE_PROGRAM", ""):
            self.build_requires("make/4.2.1")

    def _uncompress_7z(self, filename):
        self.run("7zr x {}".format(filename))

    _msvc_platforms = {
        "x86_64": "x64",
        "x86": "x86",
    }

    def _build_msvc(self):
        with tools.vcvars(self.settings):
            with tools.chdir(os.path.join("CPP", "7zip")):
                self.run("nmake /f makefile PLATFORM=%s" % (
                self._msvc_platforms[str(self.settings.arch_build)]))

    def _build_autotools(self):
        # TODO: Enable non-Windows methods in configure
        autotools = AutoToolsBuildEnvironment(self)
        extra_env = {}
        if self.settings.os_build == "Windows" and self.settings.compiler == "gcc":
            extra_env["IS_MINGW"] = "1"
        with tools.environment_append(extra_env):
            with tools.chdir(os.path.join("CPP", "7zip", "Bundles", "LzmaCon")):
                autotools.make(args=["-f", "makefile.gcc"], target="all")

    def _patch_sources(self):
        if self.settings.compiler == "Visual Studio":
            fn = os.path.join("CPP", "Build.mak")
            os.chmod(fn, 0o644)
            tools.replace_in_file(fn, "-MT", "-{}".format(str(self.settings.compiler.runtime)))
            tools.replace_in_file(fn, "-MD", "-{}".format(str(self.settings.compiler.runtime)))

    def build(self):
        self._patch_sources()
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
