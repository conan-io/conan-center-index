import os
from conans import ConanFile, CMake, tools
from fnmatch import fnmatch

class GLSLOptimizerConan(ConanFile):
    name = "glsl-optimizer"
    description = "GLSL optimizer based on Mesa's GLSL compiler. Used in Unity for mobile shader optimization."
    homepage = "https://github.com/aras-p/glsl-optimizer"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    exports_sources = "CMakeLists.txt"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _archive_dir(self):
        # the archive expands to a directory named expected-[COMMIT SHA1];
        # we'd like to put this under a stable name
        expected_dirs = [
            de for de in os.scandir(self.source_folder)
            if de.is_dir() and fnmatch(de.name, "glsl-optimizer-*")
        ]
        return expected_dirs[0].name

    def requirements(self):
        self.requires("opengl/system")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self._archive_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "src/glsl"))
        self.copy("lib/*", dst="lib", keep_path=False)
        self.copy("bin/*", dst="bin", keep_path=False)

