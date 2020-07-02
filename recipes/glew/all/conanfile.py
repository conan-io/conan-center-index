import os
import glob
from conans import ConanFile, CMake, tools

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
        os.rename("%s-%s" % (self.name, self.version), self._source_subfolder)
        if "patches" in self.conan_data:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_UTILS"] = "OFF"
        cmake.configure()
        return cmake

    def build(self):
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
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("GLEW_STATIC")
        if self.settings.os == "Windows":
            self.cpp_info.libs = ['glew32']

            if self.settings.compiler == "Visual Studio":
                if not self.options.shared:
                    self.cpp_info.libs[0] = "lib" + self.cpp_info.libs[0]

        else:
            self.cpp_info.libs = ['GLEW']

        if self.settings.build_type == "Debug":
            self.cpp_info.libs[0] += "d"

