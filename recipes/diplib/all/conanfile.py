from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain
from conan.tools.files import get

class diplibConan(ConanFile):
    name = "diplib"
    settings = "os", "compiler", "arch", "build_type"

    options = { "jpeg" : [None, "libjpeg-turbo", "libjpeg"],
                "with_glfw" : [True, False],
                "with_freeglut" : [True, False],
                "openmp" : [True, False],
                "enable_viewer" : [True, False],
                "with_zlib" : [True, False],
                "enable_ics" : [True, False],
                "with_tiff" : [True, False],
                "unicode" : [True, False],
                "always_128bit_prng" : [True, False],
                "with_fftw" : [True, False],
                "asserts" : [True, False],
                "shared" : [True, False],
                "fPIC": [True, False]
               }

    default_options = {"jpeg" : "libjpeg",
                       "with_glfw" : False,
                       "with_freeglut" : False,
                       "openmp" : True,
                       "enable_viewer" : False,
                       "with_zlib" : True,
                       "enable_ics" : True,
                       "with_tiff" : True,
                       "unicode" : True,
                       "always_128bit_prng" : False,
                       "with_fftw" : False,
                       "asserts" : False,
                       "shared" : False,
                       "fPIC" : True
                       }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        # if we don't build the viewer we don't need the backends
        if not self.options.enable_viewer:
            self.options.rm_safe("with_glfw")
            self.options.rm_safe("with_freeglut")

        if self.options.shared:
            self.options.rm_safe("fPIC")


    def requirements(self):
        #need a patch for these two, to use external
        self.requires("eigen/3.4.0")
        # libics not available in CCI but when that is we will do it too
        # self.requires("libics/??")


        if self.options.jpeg is not None:
            if self.options.jpeg == "libjpeg-turbo":
                self.requires("libjpeg-turbo/3.0.0")
            else:
                self.requires("libjpeg/9e")


        if self.options.enable_viewer:
            self.requires("opengl/system")
            if self.options.with_glfw:
                self.requires("glfw/3.3.8")
            if self.options.with_freeglut:
                self.requires("freeglut/3.4.0")

        if self.options.with_zlib:
            self.requires("zlib/1.2.13")

        if self.options.with_tiff:
            self.requires("libtiff/4.6.0")

        if self.options.with_fftw:
            self.requires("fftw/3.3.10")

    def validate_build(self):
        viewer_backend: bool = self.options.get_safe("with_glfw", False) or self.options.get_safe("with_freeglut", False)
        if self.options.enable_viewer and not viewer_backend:
            self.output.error("must enable at least one viewer backend if enable_viewer=True")
            self.output.error("you must set one or both of with_freeglut and with_glfw to True")
            raise ConanInvalidConfiguration("invalid viewer backend configuration")


    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["DIP_ENABLE_DOCTEST"] = False
        tc.cache_variables["DIP_BUILD_JAVAIO"] = False
        tc.cache_variables["DIP_BUILD_PYDIP"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()


    def build(self):
        cm = CMake(self)
        cm.configure()
        cm.build()
