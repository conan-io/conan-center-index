from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
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
    settings = "compiler", "os", "arch", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "17",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn(f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support.")
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(f"{self.name} requires C++{self._minimum_cpp_standard} support. The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*", src=os.path.join(self._source_subfolder, "include"), dst="include")

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "GLShaderPP"))
