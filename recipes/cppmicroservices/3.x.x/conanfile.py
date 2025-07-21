from conan import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import get, replace_in_file
from conan.tools.build import check_min_cppstd

import os


class CppMicroServicesConan(ConanFile):
    name = "cppmicroservices"
    description = "CppMicroServices is a C++ implementation of the OSGi spec"
    package_type = "library"
    url = "https://github.com/CppMicroServices/CppMicroServices.git"
    homepage = "https://cppmicroservices.org"
    topics = ("modularity", "runtime linking",
              "dependency inversion", "service oriented")
    license = "Apache-2.0"
    no_copy_source = True
    settings = "os", "compiler", "build_type", "arch"
    version = "3.8.7"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True
    }

    def validate(self):
        check_min_cppstd(self, 17)
        
    def build_requirements(self):
        self.tool_requires("cmake/[>=3.17]")
        
    def source(self):
        # we recover the saved url and commit from conandata.yml and use them to get sources
        git = Git(self)
        target = os.path.join(self.source_folder, "target")
        git.folder = target
        git.clone(url=self.url, args=["--recurse-submodules"], target=target)
        git.checkout(commit=(self.conan_data["sources"][self.version]["sha1"]
                             or self.conan_data["sources"][self.version]["branch"]))

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        os.environ["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        print(f"package_folder = {self.package_folder}")
        cmake = CMake(self)
        target = os.path.join(self.source_folder, "target")
        cmake.configure(variables={"US_BUILD_TESTING": "Off"},
                        build_script_folder=target)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        if self.settings.os != "Windows":
            self.cpp_info.libs = ["CppMicroServices",
                                  "DeclarativeServices", "ConfigurationAdmin"]
        else:
            self.cpp_info.libs = ["CppMicroServices3",
                                  "DeclarativeServices1", "ConfigurationAdmin1"]
        self.cpp_info.includedirs = ['include/cppmicroservices3']
        self.cpp_info.builddirs = ['share/cppmicroservices3/cmake', 'bin']
