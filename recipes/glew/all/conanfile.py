import os
import glob
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.36.0"

class GlewConan(ConanFile):
    name = "glew"
    description = "The GLEW library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://github.com/nigels-com/glew"
    topics = ("conan", "glew", "opengl", "wrangler", "loader", "binding")
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_egl": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_egl": False
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_egl

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("opengl/system")
        self.requires("glu/system")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("%s-%s" % (self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_UTILS"] = False
        self._cmake.definitions["GLEW_EGL"] = self.options.get_safe("with_egl", False)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        for pdb_file in glob.glob(os.path.join(self.package_folder, "lib", "*.pdb")):
            os.remove(pdb_file)

        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "GLEW", "cmake_find_package")
        self.cpp_info.set_property("cmake_file_name", "glew", "cmake_find_package_multi")
        self.cpp_info.set_property("cmake_target_name", "GLEW")
        self.cpp_info.components["glewlib"].set_property("cmake_target_name", "GLEW", "cmake_find_package")
        glewlib_target_name = "glew" if self.options.shared else "glew_s"
        self.cpp_info.components["glewlib"].set_property("cmake_target_name", glewlib_target_name)
        self.cpp_info.components["glewlib"].libs = tools.collect_libs(self)
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.components["glewlib"].defines.append("GLEW_STATIC")
        self.cpp_info.components["glewlib"].requires = ["opengl::opengl", "glu::glu"]
