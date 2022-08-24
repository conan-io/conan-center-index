from conans import ConanFile, tools


class HapplyConan(ConanFile):
    name = "happly"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nmwsharp/happly"
    topics = ("conan", "happly", "ply", "3D")
    license = "MIT"
    description = "A C++ header-only parser for the PLY file format. Parse .ply happily!"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("happly.h", src=self._source_subfolder, dst="include")

    def package_id(self):
        self.info.header_only()
