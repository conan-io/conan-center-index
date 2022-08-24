from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class StbConan(ConanFile):
    name = "stb"
    description = "single-file public domain libraries for C/C++"
    topics = ("stb", "single-file")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nothings/stb"
    license = ("Unlicense", "MIT")
    no_copy_source = True

    options = {
        "with_deprecated": [True, False]
    }

    default_options = {
        "with_deprecated": True
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _version(self):
        # HACK: Used to circumvent the incompatibility
        #       of the format cci.YYYYMMDD in tools.Version
        return str(self.version)[4:]

    def config_options(self):
        if tools.scm.Version(self._version) < "20210713":
            del self.options.with_deprecated

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", src=self._source_subfolder, dst="include")
        self.copy("stb_vorbis.c", src=self._source_subfolder, dst="include")
        tools.files.rmdir(self, os.path.join(self.package_folder, "include", "tests"))
        if tools.scm.Version(self._version) >= "20210713":
            tools.files.rmdir(self, os.path.join(self.package_folder, "include", "deprecated"))
        if self.options.get_safe("with_deprecated", False):
            self.copy("*.h", src=os.path.join(self._source_subfolder, "deprecated"), dst="include")
            self.copy("stb_image.c", src=os.path.join(self._source_subfolder, "deprecated"), dst="include")

    def package_id(self):
        self.info.header_only()
    
    def package_info(self):
        self.cpp_info.defines.append('STB_TEXTEDIT_KEYTYPE=unsigned')
