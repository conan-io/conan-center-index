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
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        source_data = self.conan_data["sources"][self.version]
        filename = source_data["url"].split("/")[-1]
        commit = filename.split(".")[0]
        tools.get(**source_data)
        tools.rename("godot_headers-{}".format(commit), self._source_subfolder)

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=self._source_subfolder)
        self.copy("api.json", dst="res", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
