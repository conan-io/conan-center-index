from conan import ConanFile
from conan.tools.files import get, rm, rmdir, collect_libs, copy
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain
import pathlib

def get_include_root(conanfile: ConanFile, depname: str) -> str:
    pth = pathlib.Path(conanfile.dependencies[depname].cpp_info.includedirs[0]).parent
    return str(pth)


class SImageConan(ConanFile):
    name = "simage"
    settings = "os", "arch", "compiler", "build_type"
    description = "library for loading, manipulating and saving images, movies and audio"
    license = "ISC"
    homepage = "https://www.coin3d.org/"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    topics = ("image", "video")
    options = {"shared" : [True, False],
               "with_jasper" : [True, False],
               "with_qt" : [5, 6, None],
               "fPIC" : [True, False]}

    default_options = {"shared" : False,
                       "with_jasper" : False,
                       "with_qt" : None,
                       "fPIC" : True}

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("libsndfile/1.2.2")
        self.requires("zlib/1.2.13")
        self.requires("giflib/5.2.1")
        self.requires("libjpeg/9e")
        self.requires("libpng/1.6.40")
        self.requires("libtiff/4.6.0")
        self.requires("ogg/1.3.5")
        self.requires("vorbis/1.3.7")
        if self.options.with_jasper:
            self.requires("jasper/4.0.0")
        if self.options.get_safe("with_qt", 5):
            self.requires("qt/5.15.10")
        elif self.options.get_safe("with_qt", 6):
            self.requires("qt/6.5.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SIMAGE_BUILD_EXAMPLES"] = False
        tc.cache_variables["SIMAGE_BUILD_TESTS"] = False
        tc.cache_variables["SIMAGE_BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["SIMAGE_LIBJASPER_SUPPORT"] = self.options.with_jasper

        #simage uses internal FindVorbis with non-standard target names,
        #and furthermore (weirdly) uses the CMake variables directly not targets.
        #better to set VORBIS_ROOT correctly and let it use its internal FindVorbis.cmake
        tc.cache_variables["VORBIS_ROOT"] = get_include_root(self, "vorbis")
        #same for Ogg
        tc.cache_variables["OGG_ROOT"] = get_include_root(self, "ogg")
        tc.generate()

        if self.options.with_qt is not None:
            tc.cache_variables["SIMAGE_USE_QIMAGE"] = True
            tc.cache_variables["SIMAGE_USE_QT6"] = self.options.with_qt == 6

        deps = CMakeDeps(self)
        #simage internal FindVorbis uses non-standard target names
        deps.set_property("vorbis", "cmake_find_mode", "none") 
        deps.set_property("ogg", "cmake_find_mode", "none")
        deps.generate()

    def build(self):
        cm = CMake(self)
        cm.configure()
        cm.build()

    def package(self):
        cm = CMake(self)
        cm.install()
        rm(self, "*.cmake", self.package_folder, True)
        rm(self, "*.pc", self.package_folder, True)

        # remove simage-config binary, won't work properly anyway
        # also remove installed cmake and pkg-config files
        rmdir(self, self.package_path / "share")
        rmdir(self, self.package_path / "lib" / "cmake")
        rmdir(self, self.package_path / "lib" / "pkgconfig")
        rmdir(self, self.package_path / "bin")

        license_folder = str(pathlib.Path(self.package_folder) / "licenses")
        copy(self, "COPYING", self.source_folder, license_folder)
        copy(self, "LICENSE", self.source_folder, license_folder)
        copy(self, "LICENSE.mpeg2enc", self.source_folder, license_folder)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        self.cpp_info.set_property("cmake_file_name", "simage")
        self.cpp_info.set_property("cmake_target_name", "simage::simage")
        self.cpp_info.set_property("pkg_config_name", "simage")

        #legacy cmake generators support (to be removed eventually)
        self.cpp_info.names["cmake_find_package"] = "simage"
        self.cpp_info.names["cmake_find_package_multi"] = "simage"
        self.cpp_info.names["pkg_config"] = "simage"
