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
#        tools.replace_in_file("%s/build/cmake/CMakeLists.txt" % self._source_subfolder, "include(GNUInstallDirs)",
#"""
#include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
#conan_basic_setup()
#include(GNUInstallDirs)
#""")

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

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        for pdb_file in glob.glob(os.path.join(self.package_folder, "lib", "*.pdb")):
            os.remove(pdb_file)

        self.copy("include/*", ".", "%s" % self._source_subfolder, keep_path=True)
        self.copy("%s/license*" % self._source_subfolder, dst="licenses",  ignore_case=True, keep_path=False)
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                if self.options.shared:
                    if self.settings.build_type == "Release":
                        self.copy("glew32.lib", "lib", "lib", keep_path=False)
                        self.copy("glew32.dll", "bin", "bin", keep_path=False)
                    else:
                        self.copy("glew32d.lib", "lib", "lib", keep_path=False)
                        self.copy("glew32d.dll", "bin", "bin", keep_path=False)
                else:
                    if self.settings.build_type == "Release":
                        self.copy("libglew32.lib", "lib", "lib", keep_path=False)
                    else:
                        self.copy("libglew32d.lib", "lib", "lib", keep_path=False)
            else:
                if self.options.shared:
                    self.copy(pattern="*32.dll.a", dst="lib", keep_path=False)
                    self.copy(pattern="*32d.dll.a", dst="lib", keep_path=False)
                    self.copy(pattern="*.dll", dst="bin", keep_path=False)
                else:
                    self.copy(pattern="*32.a", dst="lib", keep_path=False)
                    self.copy(pattern="*32d.a", dst="lib", keep_path=False)
        elif self.settings.os == "Macos":
            if self.options.shared:
                self.copy(pattern="*.dylib", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", keep_path=False)
        else:
            if self.options.shared:
                self.copy(pattern="*.so", dst="lib", keep_path=False)
                self.copy(pattern="*.so.*", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", keep_path=False)

    @property
    def _glew_defines(self):
        defines = []
        if self.settings.os == "Windows" and not self.options.shared:
            defines.append("GLEW_STATIC")
        return defines

    def package_info(self):
        self.cpp_info.defines = self._glew_defines
        if self.settings.os == "Windows":
            self.cpp_info.libs = ['glew32']

            if self.settings.compiler == "Visual Studio":
                if not self.options.shared:
                    self.cpp_info.libs[0] = "lib" + self.cpp_info.libs[0]

        else:
            self.cpp_info.libs = ['GLEW']

        if self.settings.build_type == "Debug":
            self.cpp_info.libs[0] += "d"

