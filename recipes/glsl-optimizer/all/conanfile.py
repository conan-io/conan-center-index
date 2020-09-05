import os
import glob
from conans import ConanFile, CMake, tools

class GLSLOptimizerConan(ConanFile):
    name = "glsl-optimizer"
    description = "GLSL optimizer based on Mesa's GLSL compiler. Used in Unity for mobile shader optimization."
    homepage = "https://github.com/aras-p/glsl-optimizer"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "glsl", "opengl")
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    exports_sources = "CMakeLists.txt"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("opengl/system")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "src/glsl"))
        self.copy("lib/*", dst="lib", keep_path=False)
        self.copy("bin/*", dst="bin", keep_path=False)

