from conan import ConanFile, tools$

class FernandoVelcicHexdumpConan(ConanFile):
    name = "fernandovelcic-hexdump"
    description = "A header-only hexdump library."
    license = ["BSD-3-Clause"]
    topics = ("hexadecimal", "hexdump", "inspection", "debug")
    homepage = "https://github.com/FernandoVelcic/hexdump"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="hexdump.hpp", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
