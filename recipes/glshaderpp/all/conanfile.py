from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"

class GLShaderPPConan(ConanFile):
    name = "glshaderpp"
    homepage = "https://gitlab-lepuy.iut.uca.fr/opengl/glshaderpp"
    description = "A lightweight header-only library to compile and link OpenGL GLSL shaders."
    topics = ("opengl", "glsl", "shader", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    license = "LGPL-3.0-or-later"
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 17)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*", src=os.path.join(self._source_subfolder, "include"), dst="include")

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "GLShaderPP"))
