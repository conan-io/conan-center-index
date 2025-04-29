from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
import os

class KahipConan(ConanFile):
    name            = "kahip"
    version         = "3.19"
    license         = "MIT"
    url             = "https://github.com/KaHIP/KaHIP"
    homepage        = url
    description     = "Karlsruhe High Quality Partitioning"
    topics          = ("graph", "partitioning", "algorithms")
    package_type    = "library"

    settings = "os", "compiler", "arch", "build_type"
    options  = {
        "shared"         : [True, False],
        "fPIC"           : [True, False],
        "python_module"  : [True, False],
    }
    default_options = {
        "shared"         : False,
        "fPIC"           : True,
        "python_module"  : False,
    }
    implements = ["auto_shared_fpic"]


    @property
    def _min_cppstd(self):
        return "11"
    
    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def requirements(self):
        if self.options.python_module:
            self.requires("pybind11/2.13.6")

    def package_id(self):
        self.info.clear()

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["NOMPI"]             = True
        tc.cache_variables["USE_TCMALLOC"]      = False
        tc.cache_variables["USE_ILP"]           = False # would require gurobi
        
        tc.cache_variables["BUILDPYTHONMODULE"] = self.options.python_module
        if self.options.python_module:
            tc.cache_variables["CMAKE_INSTALL_PYTHONDIR"] = os.path.join(self.package_folder, "python")
        
        tc.generate()
        
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = ["kahip"]
        
        # KaHIP exposes a CMake target "KaHIP::KaHIP" and installs a config file
        self.cpp_info.set_property("cmake_file_name", "KaHIP")   # <pkg>Config.cmake
        self.cpp_info.set_property("cmake_target_name", "KaHIP::KaHIP")
            
        if self.options.python_module:
            kahip_dist_package = os.path.join(self.package_folder, "python", "kahip")
            self.runenv_info.prepend_path("PYTHONPATH", kahip_dist_package)