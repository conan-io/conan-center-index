import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, save, load, chdir
from conan.tools.layout import basic_layout

class canteraRecipe(ConanFile):
    name = "cantera"
    tool_requires="scons/4.3.0"
    package_type="library"
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
    
    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def requirements(self):
        self.requires("boost/1.83.0", headers=True, libs=False, build=False, visible=False)
        self.requires("fmt/10.1.1", headers=True)
        self.requires("yaml-cpp/0.7.0")
        self.requires("eigen/3.4.0")
        self.requires("sundials/5.4.0")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        libs = ["fmt", "yaml-cpp", "eigen"]
        include_paths = []
        lib_paths = []
        for lib in libs:
            lib_info = self.dependencies[lib].cpp_info
            include_paths = include_paths + lib_info.includedirs
            lib_paths = lib_paths + lib_info.libdirs

        sundials_info = self.dependencies["sundials"].cpp_info

        opitons = {
            "libdirname": "lib",
            "python_package": "none",
            "f90_interface": "n",
            "googletest": "none",
            "versioned_shared_library": "yes",
            "prefix": self.package_folder,
            "extra_inc_dirs": os.pathsep.join(include_paths),
            "extra_lib_dirs": os.pathsep.join(lib_paths),
            "boost_inc_dir": self.dependencies["boost"].cpp_info.includedirs[0],
            "sundials_include": sundials_info.includedirs[0],
            "sundials_libdir": sundials_info.libdirs[0]
        }

        if self.settings.os == "Windows":
            opitons["toolchain"] = "msvc"

        if self.settings.build_type == "Debug":
            opitons["optimize"] = "no"
        else:
            opitons["debug"] = "no"

        escape_str = lambda x: f'"{x}"'
        scons_args = ' '.join([f"{key}={escape_str(option)}" for key, option in opitons.items()])
        save(self, os.path.join(self.source_folder, "scons_args"), scons_args)

    def build(self):
        with chdir(self, self.source_folder):
            options = load(self, "scons_args")
            self.run(f'scons build -j4 -Y "{self.source_folder}" {options}')

    def package(self):
        with chdir(self, self.source_folder):
            self.run(f'scons install -Y "{self.source_folder}"')

    def package_info(self):
        self.cpp_info.libs = ["cantera_shared"] if self.options.shared else ["cantera"]
        self.cpp_info.resdirs = ["data"]

        if self.options.shared:
            self.cpp_info.libdirs = ["bin"] if self.settings.os == "Windows" else ["share"]
        else:
            self.cpp_info.libdirs = ["lib"]
