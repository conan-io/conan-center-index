from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy
from conan.tools.scm import Git

from os.path import join


class CwtCucumberRecipe(ConanFile):
  name = "cwt-cucumber"
  license = "MIT"
  author = "Thomas Sedlmair, thomas.sedlmair@googlemail.com"
  url = "https://github.com/ThoSe1990/cucumber-cpp"
  description = "A C++20 Cucumber interpreter"
  topics = ("cpp", "bdd", "testing", "cucumber")

  generators = "CMakeDeps"
  settings = "os", "compiler", "build_type", "arch"
  options = {"shared": [True, False]}
  default_options = {"shared": False}

  def requirements(self):
    self.requires("nlohmann_json/3.10.5")

  def source(self):
    get(self, **self.conan_data["sources"][self.version], strip_root=True)

  def generate(self):
    tc = CMakeToolchain(self)
    if self.options.shared:
      tc.variables["BUILD_SHARED_LIBS"] = True
    tc.generate()

  def build(self):
    cmake = CMake(self)
    cmake.configure()
    cmake.build()

  def package(self):
    dst = join(self.package_folder, "include" )
    src = join(self.source_folder, "src")
    copy(self, "*.hpp", src, dst)

    dst = join(self.package_folder, "lib")
    src = join(self.source_folder, "lib")
    copy(self, "*", src, dst, keep_path=False)

    copy(self, "LICENSE", self.source_folder, self.package_folder)

  def package_info(self):
    self.cpp_info.libs = ["cwt-cucumber"]

    self.cpp_info.includedirs = ['include']
    self.cpp_info.libdirs = ['lib']

    self.cpp_info.components["cucumber"].set_property("cmake_target_name", "cwt::cucumber")
    self.cpp_info.components["cucumber"].libs = ["cucumber"]

    self.cpp_info.components["cucumber-no-main"].set_property("cmake_target_name", "cwt::cucumber-no-main")
    self.cpp_info.components["cucumber-no-main"].libs = ["cucumber-no-main"]
