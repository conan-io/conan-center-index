import os
from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=1.37.0"

class GlextConan(ConanFile):
    name = "glext"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.khronos.org/registry/OpenGL/index_gl.php"
    description = "OpenGL 1.2 and above compatibility profile and extension interfaces"
    topics = ("opengl", "gl", "glext")
    no_copy_source = True

    def requirements(self):
        self.requires("opengl/system")
        self.requires("khrplatform/cci.20200529")

    def source(self):
        tools.files.download(self, filename="glext.h", **self.conan_data["sources"][self.version])

    def package(self):
        self.copy(pattern="glext.h", dst=os.path.join("include", "GL"))
        license_data = tools.files.load(self, os.path.join(self.source_folder, "glext.h"))
        begin = license_data.find("/*") + len("/*")
        end = license_data.find("*/")
        license_data = license_data[begin:end]
        license_data = license_data.replace("**", "")
        tools.files.save(self, "LICENSE", license_data)
        self.copy("LICENSE", dst="licenses")

    def package_id(self):
        self.info.header_only()
