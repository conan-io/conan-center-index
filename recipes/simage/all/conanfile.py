from conan import ConanFile
from conan.tools.files import get
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain
import pathlib

def get_include_root(conanfile: ConanFile, depname: str) -> str:
    pth = pathlib.Path(conanfile.dependencies[depname].cpp_info.includedirs[0]).parent
    return str(pth)



class SImageConan(ConanFile):
    name = "simage"
    settings = "os", "arch", "compiler", "build_type"

    options = {"shared" : [True, False],
               "jasper" : [True, False]}
    default_options = {"shared" : False,
                       "jasper" : False}

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libsndfile/1.2.2")
        self.requires("zlib/1.2.13")
        self.requires("giflib/5.2.1")
        self.requires("libjpeg/9e")
        self.requires("libpng/1.6.40")
        self.requires("libtiff/4.6.0")
        self.requires("ogg/1.3.5")
        self.requires("vorbis/1.3.7")
        if self.options.jasper:
            self.requires("jasper/4.0.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SIMAGE_BUILD_EXAMPLES"] = False
        tc.cache_variables["SIMAGE_BUILD_TESTS"] = False
        tc.cache_variables["SIMAGE_BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["SIMAGE_LIBJASPER_SUPPORT"] = self.options.jasper

        #simage uses internal FindVorbis with non-standard target names,
        #and furthermore (weirdly) uses the CMake variables directly not targets.
        #better to set VORBIS_ROOT correctly and let it use its internal FindVorbis.cmake
        tc.cache_variables["VORBIS_ROOT"] = get_include_root(self, "vorbis")
        #same for Ogg
        tc.cache_variables["OGG_ROOT"] = get_include_root(self, "ogg")
        tc.generate()

        deps = CMakeDeps(self)
        #simage internal FindVorbis uses non-standard target names
        deps.set_property("vorbis", "cmake_find_mode", "none") 
        deps.set_property("ogg", "cmake_find_mode", "none")
        deps.generate()

    def build(self):
        cm = CMake(self)
        cm.configure()
        cm.build()
