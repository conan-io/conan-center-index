from conan import ConanFile, tools$
import os

required_conan_version = ">=1.43.0"


class GlmConan(ConanFile):
    name = "glm"
    description = "OpenGL Mathematics (GLM)"
    topics = ("glm", "opengl", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/g-truc/glm"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        glm_version = self.version if self.version.startswith("cci") else tools.scm.Version(self._get_semver())
        if glm_version == "0.9.8" or (glm_version == "0.9.9" and self._get_tweak_number() < 6):
            tools.files.save(self, os.path.join(self.package_folder, "licenses", "copying.txt"), self._get_license())
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
        manual = tools.files.load(self, os.path.join(self.source_folder, self._source_subfolder, "manual.md"))
        begin = manual.find("### The Happy Bunny License (Modified MIT License)")
        end = manual.find("\n![](./doc/manual/frontpage2.png)", begin)
        return manual[begin:end]

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "glm")
        self.cpp_info.set_property("cmake_target_name", "glm::glm")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
