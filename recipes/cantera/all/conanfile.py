import os

from conan import ConanFile
from conan.tools.files import get

class canteraRecipe(ConanFile):
    name = "cantera"
    tool_requires="scons/4.3.0"
    options = {
        "shared": [True, False]
    }
    default_options = {
        "shared": False
    }

    
    # Metadata
    description = "Cantera is an open-source collection of object-oriented software tools for problems involving chemical kinetics, thermodynamics, and transport processes."
    license = "LicenseRef-Cantera"
    homepage = "https://www.cantera.org/"
    topics = ("chemical kinetics", "combustion", "thermodynamics", "reacting flows", "catalysis", "electrochemistry")
    url = "https://github.com/conan-io/conan-center-index"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"

    # Define config variables
    scons_extra_inc_dirs = []
    scons_extra_lib_dirs = []
    scons_sundials_include = ""
    scons_sundials_libdir = ""
    scons_boost_inc_dir = ""

    @property
    def _min_cppstd(self):
        return 17

    def requirements(self):
        self.requires("boost/1.83.0", headers=True, libs=False, build=False, visible=False)
        self.requires("fmt/10.1.1")
        self.requires("yaml-cpp/0.7.0")
        self.requires("eigen/3.4.0")
        self.requires("sundials/5.4.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        self.scons_extra_inc_dirs = \
            self.dependencies["fmt"].cpp_info.includedirs +\
            self.dependencies["yaml-cpp"].cpp_info.includedirs +\
            self.dependencies["eigen"].cpp_info.includedirs
        
        self.scons_extra_lib_dirs = \
            self.dependencies["fmt"].cpp_info.libdirs +\
            self.dependencies["yaml-cpp"].cpp_info.libdirs +\
            self.dependencies["eigen"].cpp_info.libdirs
        
        self.scons_sundials_include = self.dependencies["sundials"].cpp_info.includedirs[0]
        self.scons_sundials_libdir = self.dependencies["sundials"].cpp_info.libdirs[0]
        
        self.scons_boost_inc_dir = self.dependencies["boost"].cpp_info.includedirs[0]

    def layout(self):
        self.folders.source = "."
        self.folders.build = "build"
        self.cpp.source.includedirs = ["include"]

    def build(self):

        if self.settings.os == "Windows":
            opt = "toolchain=msvc "
            cd_modifier = "/d"
        else:
            opt = ""
            cd_modifier = ""

        opt = opt +\
              "prefix={} ".format(self.package_folder) +\
              "libdirname=lib " \
              "python_package=none " \
              "f90_interface=n " \
              "googletest=none " \
              "versioned_shared_library=yes " \
              "extra_inc_dirs={} ".format(os.pathsep.join(self.scons_extra_inc_dirs)) +\
              "extra_lib_dirs={} ".format(os.pathsep.join(self.scons_extra_lib_dirs)) +\
              "boost_inc_dir={} ".format(self.scons_boost_inc_dir) +\
              "sundials_include={} ".format(self.scons_sundials_include) +\
              "sundials_libdir={} ".format(self.scons_sundials_libdir)

        if self.settings.build_type == "Debug":
            opt = opt + "optimize=no "
        else:
            opt = opt + "debug=no "

        self.run("cd {} {} && scons build -j4 {}".format(cd_modifier, self.source_folder, opt))

    def package(self):
        if self.settings.os == "Windows":
            cd_modifier = "/d"
        else:
            cd_modifier = ""
        
        self.run("cd {} {} && scons install".format(cd_modifier, self.source_folder))

    
    def package_info(self):
        self.cpp_info.libs = ["cantera_shared"] if self.options.shared else ["cantera"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["bin"] if self.options.shared else ["lib"]
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.resdirs = ["data"]
