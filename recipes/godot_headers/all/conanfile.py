import glob
from conans import ConanFile, tools


class GodotHeadersConan(ConanFile):
    name = "godot_headers"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/godotengine/godot_headers"
    description = "Godot Native interface headers"
    topics = ("game-engine", "game-development")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        tools.files.rename(self, glob.glob("godot-headers-*")[0], self._source_subfolder)

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=self._source_subfolder)
        self.copy("api.json", dst="res", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
