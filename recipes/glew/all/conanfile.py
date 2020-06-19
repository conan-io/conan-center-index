import os
from conans import ConanFile, CMake, tools

class GlewConan(ConanFile):
    name = "glew"
    description = "The GLEW library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://github.com/nigels-com/glew"
    topics = ("conan", "glew", "opengl", "wrangler", "loader", "binding")
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    _source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires("opengl/system")
        self.requires("glu/system")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("glew-" + self.version, self._source_subfolder)

        tools.replace_in_file(
            file_path=os.path.join(self._source_subfolder, "build", "cmake", "CMakeLists.txt"),
            search="target_link_libraries (glew LINK_PRIVATE -nodefaultlib -noentry)",
            replace="target_link_libraries (glew LINK_PRIVATE -nodefaultlib -noentry libvcruntime.lib msvcrt.lib)"
        )

    @property
    def _glew_defines(self):
        defines = []
        if self.settings.os == "Windows" and not self.options.shared:
            defines.append("GLEW_STATIC")
        return defines

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_UTILS"] = "OFF"
        cmake.definitions["CONAN_GLEW_DEFINITIONS"] = ";".join(self._glew_defines)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "GLEW"
        self.cpp_info.names["cmake_find_package_multi"] = "GLEW"

        self.cpp_info.defines = self._glew_defines
        self.cpp_info.libs = tools.collect_libs(self)
