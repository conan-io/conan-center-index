import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.28.0"

class LibosmscoutConan(ConanFile):
    name = "libosmscout"
    license = "LGPL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Framstag/libosmscout"
    description = "Libosmscout is a C++ library for offline map rendering, routing and location lookup based on OpenStreetMap data"
    topics = ("navigation", "map", "osm")
    exports_sources = "patches/**", "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
    short_paths = True
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _supports_cpp17(self):
        supported_compilers = [("gcc", "7"), ("clang", "5"), ("apple-clang", "10"), ("Visual Studio", "15")]
        compiler = self.settings.compiler
        version = tools.Version(compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        elif not self._supports_cpp17():
            raise ConanInvalidConfiguration("libosmscout requires C++17 support")

    def requirements(self):
        self.requires("libiconv/1.16")
        self.requires("libxml2/2.9.12")
        self.requires("protobuf/3.9.1")
        self.requires("cairo/1.17.4")
        self.requires("pango/1.48.7")
        self.requires("freetype/2.10.4")
        self.requires("opengl/system")
        self.requires("freeglut/3.2.1")
        self.requires("glm/0.9.9.8")
        self.requires("glew/2.2.0")
        self.requires("glib/2.69.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["OSMSCOUT_BUILD_CLIENT_QT"] = False
        self._cmake.definitions["OSMSCOUT_BUILD_TOOL_IMPORT"] = False
        self._cmake.definitions["OSMSCOUT_BUILD_TOOL_IMPORT"] = False
        self._cmake.definitions["OSMSCOUT_BUILD_TOOL_DUMPDATA"] = False
        self._cmake.definitions["OSMSCOUT_BUILD_TOOL_PUBLICTRANSPORTMAP"] = False
        self._cmake.definitions["OSMSCOUT_BUILD_TOOL_OSMSCOUT2"] = False
        self._cmake.definitions["OSMSCOUT_BUILD_TOOL_OSMSCOUTOPENGL"] = False
        self._cmake.definitions["OSMSCOUT_BUILD_TOOL_STYLEEDITOR"] = False
        self._cmake.definitions["OSMSCOUT_BUILD_DEMOS"] = False
        self._cmake.definitions["OSMSCOUT_BUILD_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share", "cmake"))

    def package_info(self):
        suffix = "d" if self.settings.build_type == "Debug" else ""
        if not self.options.shared:
            self.cpp_info.defines.append("OSMSCOUT_STATIC")
        self.cpp_info.libs = ["osmscout{}{}".format("_"+lib if lib else "", suffix)
            for lib in ["import", "map_svg", "map_cairo", "map", ""]
        ]
