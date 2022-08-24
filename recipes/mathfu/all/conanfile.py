from conans import ConanFile, tools
import os


class MathfuConan(ConanFile):
    name = "mathfu"
    description = "C++ math library developed primarily for games focused on simplicity and efficiency."
    topics = ("conan", "mathfu", "math", "geometry")
    license = "Apache-2.0"
    homepage = "https://github.com/google/mathfu"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("vectorial/cci.20190628")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
