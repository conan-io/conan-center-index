from conans import ConanFile, CMake, tools
import os

class Morphotree(ConanFile):
  name = "morphotree"
  version = "1.0.0"
  license = "MIT license"
  description = "A morphological tree prototyping library"
  settings = "os", "compiler", "build_type", "arch"
  options = {"shared": [True, False]}
  default_options = {"shared": False}
  generators = "cmake"

  def source(self):
    tools.get(**self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

  def export_sources(self):
    self.copy("*.cpp", dst="src", src="src", excludes="main.cpp")
    self.copy("CMakeLists.txt", dst="src", src="src", excludes="main.cpp")
    self.copy("*.hpp", dst="include", src="include")

  def build(self):
    cmake = CMake(self)
    cmake.configure(source_folder="src")
    cmake.build()

  def package(self):
    self.copy("*.hpp", dst="include", src="include")
    self.copy("*.lib", dst="lib", keep_path=False)
    self.copy("*.dll", dst="bin", keep_path=False)
    self.copy("*.dylib", dst="lib", keep_path=False)
    self.copy("*.so", dst="lib", keep_path=False)
    self.copy("*.a", dst="lib", keep_path=False)

  def package_info(self):
    self.cpp_info.libs = ["morphotree"]