from conan import ConanFile
from conan.tools.files import copy, get, load, save
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class GlmConan(ConanFile):
    name = "glm"
    description = "OpenGL Mathematics (GLM)"
    topics = ("glm", "opengl", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/g-truc/glm"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        glm_version = self.version if self.version.startswith("cci") else Version(self._get_semver())
        if glm_version == "0.9.8" or (glm_version == "0.9.9" and self._get_tweak_number() < 6):
            save(self, os.path.join(self.package_folder, "licenses", "copying.txt"), self._get_license())
        else:
            copy(self, "copying.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        for headers in ("*.hpp", "*.inl", "*.h"):
            copy(self, headers, src=os.path.join(self.source_folder, "glm"),
                                dst=os.path.join(self.package_folder, "include", "glm"))

    def _get_semver(self):
        return self.version.rsplit(".", 1)[0]

    def _get_tweak_number(self):
        return int(self.version.rsplit(".", 1)[-1])

    def _get_license(self):
        manual = load(self, os.path.join(self.source_folder, "manual.md"))
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
