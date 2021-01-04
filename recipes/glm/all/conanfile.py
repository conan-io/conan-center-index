from conans import ConanFile, tools
import os


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
        headers_src_dir = os.path.join(self.source_folder, self._source_subfolder, "glm")
        self.copy("*.hpp", dst=os.path.join("include", "glm"), src=headers_src_dir)
        self.copy("*.inl", dst=os.path.join("include", "glm"), src=headers_src_dir)
        self.copy("*.h", dst=os.path.join("include", "glm"), src=headers_src_dir)

    def _get_semver(self):
        return self.version.rsplit(".", 1)[0]

    def _get_tweak_number(self):
        return int(self.version.rsplit(".", 1)[-1])

    def _get_license(self):
        manual = tools.load(os.path.join(self.source_folder, self._source_subfolder, "manual.md"))
        begin = manual.find("### The Happy Bunny License (Modified MIT License)")
        end = manual.find("\n![](./doc/manual/frontpage2.png)", begin)
        return manual[begin:end]
