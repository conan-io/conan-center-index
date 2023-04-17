from conan import ConanFile
from conan.tools.files import copy, get, load, save
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class OpenGLRegistryConan(ConanFile):
    name = "opengl-registry"
    description = "OpenGL, OpenGL ES, and OpenGL ES-SC API and Extension Registry."
    license = "Apache-2.0"
    topics = ("opengl-registry", "opengl")
    homepage = "https://github.com/KhronosGroup/OpenGL-Registry"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("khrplatform/cci.20200529")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        license_data = load(self, os.path.join(self.source_folder, "api", "GL", "glext.h"))
        begin = license_data.find("/*") + len("/*")
        end = license_data.find("*/")
        license_data = license_data[begin:end]
        license_data = license_data.replace("**", "")
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_data)

        copy(self, "*", src=os.path.join(self.source_folder, "api"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*", src=os.path.join(self.source_folder, "xml"), dst=os.path.join(self.package_folder, "res", "xml"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
