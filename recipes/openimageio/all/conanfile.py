from conans import ConanFile, CMake, tools
import os

class OpenImageIOConan(ConanFile):
    name = "openimageio"
    description = "OpenImageIO is a library for reading and writing images, and a bunch of related classes, utilities, and applications." \
                  "There is a particular emphasis on formats and functionality used in professional, large-scale animation and visual effects work for film."
    topics = ("conan", "vfx", "image", "picture")
    license = "BSD-3-Clause"
    homepage = "http://www.openimageio.org/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/*"]

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_dcmtk": [True, False],
        "with_raw": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_dcmtk": False, # Heavy dependency, disabled by default
        "with_raw": False # libraw is available under CDDL-1.0 or LGPL-2.1, for this reason it is disabled by default
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _install_folder(self):
        return os.path.join(self.build_folder, "install")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)

        # CMake options
        self._cmake.definitions["OIIO_BUILD_TOOLS"] = True
        self._cmake.definitions["OIIO_BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_DOCS"] = False
        self._cmake.definitions["INSTALL_DOCS"] = False
        self._cmake.definitions["INSTALL_FONTS"] = False
        self._cmake.definitions["INSTALL_CMAKE_HELPER"] = False
        self._cmake.definitions["EMBEDPLUGINS"] = True
        self._cmake.definitions["USE_PYTHON"] = False
        self._cmake.definitions["USE_EXTERNAL_PUGIXML"] = True

        # Pass version variables used by OIIO's build system
        self._cmake.definitions["Boost_VERSION"] = self.deps_cpp_info["boost"].version
        self._cmake.definitions["OPENJPEG_VERSION"] = self.deps_cpp_info["openjpeg"].version
        
        self._cmake.configure()
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("openexr/2.5.2")
        self.requires("libtiff/4.1.0")
        self.requires("fmt/6.2.1")
        self.requires("boost/1.73.0")
        self.requires("tsl-robin-map/0.6.3")
        self.requires("pugixml/1.10")
        self.requires("libsquish/1.15")
        self.requires("libpng/1.6.37")
        self.requires("libjpeg-turbo/2.0.4")
        self.requires("libwebp/1.1.0")
        self.requires("openjpeg/2.3.1")
        # TODO code using GifLib 5.1.4 does not compile with Clang
        # self.requires("giflib/5.1.4")
        self.requires("freetype/2.10.2")
    
        if self.options.with_dcmtk:
            self.requires("dcmtk/3.6.5")

        if self.options.with_raw:
            self.requires("libraw/0.19.5")
        
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("oiio-Release-{}".format(self.version), self._source_subfolder)

        patch_file = os.path.join(self.source_folder, "patches", "{}.patch".format(self.version))
        tools.patch(base_path=self._source_subfolder, patch_file=patch_file, strip=1)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "include", "OpenImageIO", "fmt"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "OpenImageIO"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenImageIO"
        self.cpp_info.names['pkg_config'] = 'OpenImageIO'

        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")

        if not self.options.shared:
            self.cpp_info.defines.append("OIIO_STATIC_DEFINE")
