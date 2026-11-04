import os
import shutil

from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class DepotToolsConan(ConanFile):
    name = "depot_tools"
    description = "Tools for working with Chromium development."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://chromium.googlesource.com/chromium/tools/depot_tools"
    topics = ("chromium", "pre-built")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def _dereference_symlinks(self):
        """
        Windows 10 started to introduce support for symbolic links. Unfortunately
        it caused a lot of trouble during packaging. Namely, opening symlinks causes
        `OSError: Invalid argument` rather than actually following the symlinks.
        Therefore, this workaround simply copies the destination file over the symlink
        """
        if self.settings.os != "Windows":
            return

        for root, dirs, files in os.walk(self.source_folder):
            symlinks = [os.path.join(root, f) for f in files if os.path.islink(os.path.join(root, f))]
            for symlink in symlinks:
                dest = os.readlink(symlink)
                os.remove(symlink)
                shutil.copy(os.path.join(root, dest), symlink, follow_symlinks=False)
                self.output.info("Replaced symlink '%s' with its destination file '%s'" % (symlink, dest))

    def build(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder)
        self._dereference_symlinks()
        apply_conandata_patches(self)

    def _fix_permissions(self):
        if self.settings.os == "Windows":
            return

        def chmod_plus_x(name):
            os.chmod(name, os.stat(name).st_mode | 0o111)

        for root, _, files in os.walk(self.package_folder):
            for file_it in files:
                filename = os.path.join(root, file_it)
                with open(filename, "rb") as f:
                    sig = tuple(f.read(4))
                if len(sig) >= 2 and sig[0] == 0x23 and sig[1] == 0x21:
                    self.output.info(f"chmod on script file {file_it}")
                    chmod_plus_x(filename)
                elif sig == (0x7F, 0x45, 0x4C, 0x46):
                    self.output.info(f"chmod on ELF file {file_it}")
                    chmod_plus_x(filename)
                elif sig in [
                    (0xCA, 0xFE, 0xBA, 0xBE),
                    (0xBE, 0xBA, 0xFE, 0xCA),
                    (0xFE, 0xED, 0xFA, 0xCF),
                    (0xCF, 0xFA, 0xED, 0xFE),
                    (0xFE, 0xED, 0xFA, 0xCE),
                    (0xCE, 0xFA, 0xED, 0xFE),
                ]:
                    self.output.info(f"chmod on Mach-O file {file_it}")
                    chmod_plus_x(filename)

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*",
             dst=os.path.join(self.package_folder, "bin"),
             src=self.source_folder)
        self._fix_permissions()

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        self.runenv_info.define("DEPOT_TOOLS_UPDATE", "0")
        self.buildenv_info.define("DEPOT_TOOLS_UPDATE", "0")

        # TODO: Legacy, to be removed on Conan 2.0
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH env var with : {bin_path}")
        self.env_info.PATH.append(bin_path)
        self.env_info.DEPOT_TOOLS_UPDATE = "0"
