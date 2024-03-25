from conan import ConanFile
from conan.tools.cmake import CMakeDeps, CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get

class VigraConan(ConanFile):
    name = "vigra"
    description = "A generic C++ library for image analysis"
    license = "MIT"
    url = "https://github.com/ukoethe/vigra"
    homepage = "http://ukoethe.github.io/vigra/"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared" : [True, False],
        "with_hdf5" : [True, False],
        "with_openexr" : [True, False],
        "with_boost_graph" : [True, False]
        }

    default_options = {"shared" : False,
                       "with_hdf5": True,
                       "with_openexr" : True,
                       "with_boost_graph" : True}


    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

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

        #override since current openexr breaks this
        self.requires("libdeflate/1.19", override=True)


    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["WITH_VIGRANUMPY"] = False

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cm = CMake(self)
        cm.configure()

        cm.build()

