from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain
from conan.tools.files import get, collect_libs
from conan.tools.build import check_min_cppstd
import os


class diplibConan(ConanFile):
    name = "diplib"
    settings = "os", "compiler", "arch", "build_type"

    options = {
        # options that control which external dependencies are used
        "with_fftw" : [True, False],
        "with_freeglut" : [True, False],
        "with_freetype" : [True, False],
        "with_glfw" : [True, False],
        "jpeg" : [None, "libjpeg-turbo", "libjpeg"],
        "with_libtiff" : [True, False],
        "with_zlib" : [True, False],

        # options that build extra functionality into the library,
        # but do not need extra external dependencies to do so
        "enable_ics" : [True, False],
        "enable_viewer" : [True, False],


        # options that change behaviour of the library
        "always_128bit_prng" : [True, False],
        "asserts" : [True, False],
        "multithreading" : [True, False],
        "stack_trace" : [True, False],
        "unicode" : [True, False],

        #standard build options
        "fPIC": [True, False],
        "shared" : [True, False],


    }

    default_options = { "with_fftw" : False,
                        "with_freeglut" : True,
                        "with_freetype" : False,
                        "with_glfw" : True,
                        "jpeg" : "libjpeg",
                        "with_libtiff" : True,
                        "with_zlib" : True,

                        "enable_ics" : True,
                        "enable_viewer" : False,

                        "always_128bit_prng" : False,
                        "asserts" : False,
                        "multithreading" : True,
                        "stack_trace" : True,
                        "unicode" : True,

                        "fPIC" : True,
                        "shared" : False,

                       }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        #on macOSX, we should set the default to be without freeglut,
        #because that's what the CMakeLists.txt does. On other platforms it's True
        if self.settings.os == "Macos":
            self.options.with_freeglut = False

    def configure(self):
        # if we don't build the viewer we don't need the backends
        if not self.options.enable_viewer:
            self.options.rm_safe("with_glfw")
            self.options.rm_safe("with_freeglut")

        if self.options.shared:
            self.options.rm_safe("fPIC")


    def requirements(self):
        self.requires("eigen/3.4.0")
        # libics not available in CCI but when that is we will add it below too


        if self.options.jpeg is not None:
            if self.options.jpeg == "libjpeg-turbo":
                self.requires("libjpeg-turbo/3.0.0")
            else:
                self.requires("libjpeg/9e")

        #if we're not building viewer, don't want any backends
        if self.options.enable_viewer:
            self.requires("opengl/system")
            if self.options.with_glfw:
                self.requires("glfw/3.3.8")
            if self.options.with_freeglut:
                self.requires("freeglut/3.4.0")

        libversions = {
            "fftw" : "3.3.10",
            "freetype" : "2.13.0",
            "libtiff" : "4.6.0",
            "zlib" : "1.2.13"}                       

        for name, version in libversions.items():
            if getattr(self.options, f"with_{name}"):
                self.requires(f"{name}/{version}")


    def validate_build(self):

        #check that if we're building viewer, we have at least one backend selected
        viewer_backend: bool = self.options.get_safe("with_glfw", False) or self.options.get_safe("with_freeglut", False)
        
        if self.options.enable_viewer and not viewer_backend:
            self.output.error("must enable at least one viewer backend if enable_viewer=True")
            self.output.error("you must set one or both of with_freeglut and with_glfw to True")
            raise ConanInvalidConfiguration("invalid viewer backend configuration")

        check_min_cppstd(self, 14)


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

        feat_cmake_map = {
            "with_fftw" : "DIP_ENABLE_FFTW",
            "with_freeglut": "DIP_FIND_FREEGLUT",
            "with_freetype" : "DIP_ENABLE_FREETYPE",
            "with_glfw" : "DIP_FIND_GLFW",
            "jpeg" :  "DIP_ENABLE_JPEG",
            "with_libtiff" : "DIP_ENABLE_TIFF",
            "with_zlib" : "DIP_ENABLE_ZLIB",

            "enable_ics" : "DIP_ENABLE_ICS",

            "always_128bit_prng" : "DIP_ALWAYS_128_PRNG",
            "asserts" : "DIP_ENABLE_ASSERT",
            "multithreading" : "DIP_ENABLE_MULTITHREADING",
            "stack_trace" : "DIP_ENABLE_STACK_TRACE",
            "unicode" : "DIP_ENABLE_UNICODE",

            "shared" : "DIP_SHARED_LIBRARY",
                          }

        for opt, cmval in feat_cmake_map.items():
            tc.cache_variables[cmval] = bool(self.options.get_safe(opt, False))

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _get_cmakecache_value(self, val: str) -> bool:
        cachepath = os.path.join(self.build_folder, "CMakeCache.txt")
        with open("CMakeCache.txt", "r") as f:
            for line in f:
                if val in line and "//" not in line:
                    valuestr = line.split("=")[1].strip()
                    if valuestr not in ["ON", "OFF", "TRUE", "FALSE", "1", "0"]:
                        raise RuntimeError(f"failed to parse  value: {valuestr}")
                    value: bool = valuestr in ["ON", "TRUE", "1"]
                    break
            else:
                raise RuntimeError(f"didn't find variable {val}  in the cmake cache")

        return value


    def build(self):
        cm = CMake(self)
        cm.configure()

        # Check that we got the right logic for building the viewer
        # doing this check defensively because it's only indirectly activated
        # when we don't feed it openGL etc etc
        viewerbuild = self._get_cmakecache_value("DIP_BUILD_DIPVIEWER")
        if viewerbuild != self.options.enable_viewer:
            raise ValueError("mismatch between CMake viewer build setting and recipe option setting")

        cm.build()

    def package(self):
        cm = CMake(self)
        cm.install()

        # #these need to go into the package id
        # self._rng_128 = self._get_cmakecache_value("HAS_128_INT")
        # self.output.info(f"128 bit generator configured? {self._rng_128}")
        # self._pretty_function = self._get_cmakecache_value("HAS_PRETTY_FUNCTION")
        # self.output.info(f"pretty functions present? {self._pretty_function}")

    def package_info(self):
        self.cpp_info.libs = collect_libs()
        
        #read the compile definitions from cmake file
        
        
