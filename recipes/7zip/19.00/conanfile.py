from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, chdir, download, get, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeToolchain
from conan.tools.scm import Version

import os

required_conan_version = ">=1.55.0"


class SevenZipConan(ConanFile):
    name = "7zip"
    url = "https://github.com/conan-io/conan-center-index"
    description = "7-Zip is a file archiver with a high compression ratio"
    license = ("LGPL-2.1", "BSD-3-Clause", "Unrar")
    homepage = "https://www.7-zip.org"
    topics = ("7zip", "zip", "compression", "decompression")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Only Windows supported")
        if self.settings.arch not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration("Unsupported architecture")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if Version(self.version) < "22":
            self.build_requires("lzma_sdk/9.20")

        if not is_msvc(self) and self._settings_build.os == "Windows" and "make" not in os.environ.get("CONAN_MAKE_PROGRAM", ""):
            self.build_requires("make/4.3")

    def package_id(self):
        del self.info.settings.build_type
        del self.info.settings.compiler

    def source(self):
        if Version(self.version) < "22":
            from six.moves.urllib.parse import urlparse
            url = self.conan_data["sources"][self.version]["url"]
            filename = os.path.basename(urlparse(url).path)
            sha256 = self.conan_data["sources"][self.version]["sha256"]
            download(self, url, filename, sha256)
            self.run(f"7zr x {filename}")
            os.unlink(filename)
        else:
            get(self, **self.conan_data["sources"][self.version])

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            if self.settings.os == "Windows" and self.settings.compiler == "gcc":
                tc.environment().define("IS_MINGW")
            tc.generate()
            deps = AutotoolsDeps(self)
            deps.generate()

    @property
    def _msvc_platform(self):
        return {
            "x86_64": "x64",
            "x86": "x86",
        }[str(self.settings.arch)]

    def _build_msvc(self):
        self.run(f"nmake /f makefile PLATFORM={self._msvc_platform}", cwd=os.path.join(self.source_folder, "CPP", "7zip"))

    def _build_autotools(self):
        # TODO: Enable non-Windows methods in configure
        autotools = Autotools(self)
        with chdir(self, os.path.join(self.source_folder, "CPP", "7zip", "Bundles", "LzmaCon")):
            autotools.make(args=["-f", "makefile.gcc"], target="all")

    def _patch_sources(self):
        if is_msvc(self):
            fn = os.path.join(self.source_folder, "CPP", "Build.mak")
            os.chmod(fn, 0o644)
            replace_in_file(self, fn, "-MT", f"-{self.settings.compiler.runtime}")
            replace_in_file(self, fn, "-MD", f"-{self.settings.compiler.runtime}")

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        copy(self, "License.txt", dst=os.path.join(self.package_folder, "licenses"), src=os.path.join(self.source_folder, "DOC"))
        copy(self, "unRarLicense.txt", dst=os.path.join(self.package_folder, "licenses"), src=os.path.join(self.source_folder, "DOC"))
        if self.settings.os == "Windows":
            copy(self, "*.exe", dst=os.path.join(self.package_folder, "bin"), src=os.path.join(self.source_folder, "CPP", "7zip"), keep_path=False)
            copy(self, "*.dll", dst=os.path.join(self.package_folder, "bin"), src=os.path.join(self.source_folder, "CPP", "7zip"), keep_path=False)
        # TODO: Package the libraries: binaries and headers (add the rest of settings)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.path.append(bin_path)
        
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
