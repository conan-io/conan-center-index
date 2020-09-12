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
    exports_sources = "CMakeLists.txt", "patches/*"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("getopt-for-visual-studio/20200201")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = CMake(self)
        cmake.configure()
        # All but tests are built, see CMakeLists.txt for details
        cmake.build()

    def package(self):
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)
        self.copy("glsl_optimizer.h", dst="include", src=os.path.join(self._source_subfolder, "src/glsl"))
        self.copy("*", src="bin", dst="bin", keep_path=False)
        self.copy("*.dll", src="bin", dst="bin", keep_path=False)
        self.copy("*.lib", src="lib", dst="lib", keep_path=False)
        self.copy("*.a", src="lib", dst="lib", keep_path=False)
        self.copy("*.so*", src="lib", dst="lib", keep_path=False)
        self.copy("*.dylib", src="lib", dst="lib", keep_path=False)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH env var with: {bin_path}")
        self.env_info.PATH.append(bin_path)

        if self.settings.os == "Windows":
            self.cpp_info.libs += ["mesa.lib", "glcpp-library.lib", "glsl_optimizer.lib"]
        else:
            self.cpp_info.libs += ["libmesa.a", "libglcpp-library.a", "libglsl_optimizer.a"]

