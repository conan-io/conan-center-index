from conan import ConanFile
from conan.tools.files import copy, get, rmdir
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class StbConan(ConanFile):
    name = "stb"
    description = "single-file public domain libraries for C/C++"
    topics = ("stb", "single-file")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nothings/stb"
    license = ("Unlicense", "MIT")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = {
        "with_deprecated": [True, False],
    }

    default_options = {
        "with_deprecated": True,
    }

    @property
    def _version(self):
        # HACK: Used to circumvent the incompatibility
        #       of the format cci.YYYYMMDD in tools.Version
        return str(self.version)[4:]

    def config_options(self):
        if Version(self._version) < "20210713":
            del self.options.with_deprecated

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        # Can't call self.info.clear() because options contribute to package id
        self.info.settings.clear()
        self.info.requires.clear()
        try:
            # conan v2 specific
            self.info.conf.clear()
        except AttributeError:
            pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        copy(self, "stb_vorbis.c", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "include", "tests"))
        if Version(self._version) >= "20210713":
            rmdir(self, os.path.join(self.package_folder, "include", "deprecated"))
        if self.options.get_safe("with_deprecated"):
            copy(self, "*.h", src=os.path.join(self.source_folder, "deprecated"), dst=os.path.join(self.package_folder, "include"))
            copy(self, "stb_image.c", src=os.path.join(self.source_folder, "deprecated"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.defines.append("STB_TEXTEDIT_KEYTYPE=unsigned")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
