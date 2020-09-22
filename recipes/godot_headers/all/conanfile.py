from conans import ConanFile
from conans import tools


class GodotHeadersConan(ConanFile):
    name = "godot_headers"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/godotengine/godot_headers"
    description = "Godot Native interface headers"
    topics = ("game-engine", "game-development")
    no_copy_source = True

    @property
    def _source_directory(self):
        return "godot_headers-{}".format(self.version)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_directory)
        self.copy("*.h", dst="include", src=self._source_directory)
        self.copy("api.json", dst="res", src=self._source_directory)

    def package_id(self):
        self.info.header_only()
