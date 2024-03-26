from conan import ConanFile
from conan.tools.cmake import CMakeDeps, CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get, apply_conandata_patches, rm, collect_libs
import pathlib

class VigraConan(ConanFile):
    name = "vigra"
    description = "A generic C++ library for image analysis"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://ukoethe.github.io/vigra/"
    settings = "os", "arch", "compiler", "build_type"
    topics = "image-processing", "computer-vision"
    options = {
        "shared" : [True, False],
        "fPIC" : [True, False],
        "with_hdf5" : [True, False],
        "with_openexr" : [True, False],
        "with_boost_graph" : [True, False],
        "with_lemon" : [True, False]
        }

    default_options = {"shared" : False,
                       "fPIC" : True,
                       "with_hdf5": True,
                       "with_openexr" : True,
                       "with_boost_graph" : True,
                       "with_lemon" : True}

    exports_sources = "patches/*.patch"

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        
    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        
    def requirements(self):
        self.requires("libtiff/4.6.0")
        self.requires("libpng/1.6.43")
        self.requires("fftw/3.3.10")

        if self.options.with_hdf5:
            self.requires("hdf5/1.14.3")

        if self.options.with_openexr:
            self.requires("openexr/3.2.3")

        if self.options.with_boost_graph:
            self.requires("boost/1.84.0")

        if self.options.with_lemon:
            self.requires("coin-lemon/1.3.1")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["WITH_VIGRANUMPY"] = False
        tc.cache_variables["BUILD_DOCS"] = False
        tc.cache_variables["BUILD_TESTS"] = False

        tc.cache_variables["WITH_OPENEXR"] = self.options.with_openexr
        tc.cache_variables["WITH_BOOST_GRAPH"] = self.options.with_boost_graph
        tc.cache_variables["WITH_LEMON"] = self.options.with_lemon

        tc.cache_variables["VIGRA_STATIC_LIB"] = not self.options.shared
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cm = CMake(self)

        cm.configure()
        cm.build()

    def package(self):
        cm = CMake(self)
        cm.install()

        #remove generated cmake packages
        rm(self, "*.cmake", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.set_property("cmake_file_name", "Vigra")
        self.cpp_info.set_property("cmake_target_name", "vigraimpex")
