from conan import ConanFile
from conan.tools.files import copy, get, load, save
from conan.tools.layout import basic_layout
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=1.50.0"


class GliConan(ConanFile):
    name = "gli"
    description = "OpenGL Image (GLI)"
    topics = ("opengl", "image")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/g-truc/gli"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glm/cci.20230113", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "copying.txt"), self._get_license())
        for headers in ("*.hpp", "*.inl", "*.h"):
            copy(self, headers, src=os.path.join(self.source_folder, "gli"),
                                dst=os.path.join(self.package_folder, "include", "gli"))

    def _get_license(self):
        manual = load(self, os.path.join(self.source_folder, "manual.md"))
        begin = manual.find("### The Happy Bunny License (Modified MIT License)")
        end = manual.find("\n![](https://github.com/g-truc/glm/blob/manual/doc/manual/frontpage2.png)", begin)
        return manual[begin:end]

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "gli")
        self.cpp_info.set_property("cmake_target_name", "gli::gli")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
