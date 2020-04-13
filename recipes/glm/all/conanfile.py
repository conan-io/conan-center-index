from conans import ConanFile, tools
import os
from distutils.dir_util import copy_tree


class GlmConan(ConanFile):
    name = "glm"
    description = "OpenGL Mathematics (GLM)"
    topics = ("conan", "glm", "opengl", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/g-truc/glm"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        if tools.Version(self._get_semver()) < "0.9.9" or \
           (tools.Version(self._get_semver()) == "0.9.9" and self._get_tweak_number() < 6):
            tools.save(os.path.join(self.package_folder, "licenses", "copying.txt"), self._get_license())
        else:
            self.copy("copying.txt", dst="licenses", src=self._source_subfolder)
        copy_tree(os.path.join(self.source_folder, self._source_subfolder, "glm"),
                  os.path.join(self.package_folder, "include", "glm"))

    def _get_semver(self):
        return self.version.rsplit(".", 1)[0]

    def _get_tweak_number(self):
        return int(self.version.rsplit(".", 1)[-1])

    def _get_license(self):
        manual = tools.load(os.path.join(self.source_folder, self._source_subfolder, "manual.md"))
        begin = manual.find("### The Happy Bunny License (Modified MIT License)")
        end = manual.find("\n![](./doc/manual/frontpage2.png)", begin)
        return manual[begin:end]
