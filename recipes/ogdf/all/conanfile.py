from conan import ConanFile
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from os.path import join

required_conan_version = ">=1.53.0"


class OGDFConan(ConanFile):
    name = "ogdf"
    description = "Open Graph algorithms and Data structures Framework"
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ogdf.net"
    topics = ("graph", "algorithm", "data-structures")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        if cross_building(self):
            raise ConanInvalidConfiguration(
                f"Cross-building is not supported: "
                f"build={self.settings_build.os}/{self.settings_build.arch}, "
                f"host={self.settings.os}/{self.settings.arch}"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("coin-clp/1.17.7")
        self.requires("pugixml/1.15")
        self.requires("earcut/2.2.4")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["COIN_SOLVER"] = "CLP"
        tc.variables["COIN_SOLVER_IS_EXTERNAL"] = 0
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        # delete code from other cci packages
        rmdir(self, join(self.source_folder, "src", "coin"))
        rmdir(self, join(self.source_folder, "include", "coin"))
        rmdir(self, join(self.source_folder, "include", "ogdf", "lib", "backward"))
        rmdir(self, join(self.source_folder, "src", "ogdf", "lib", "pugixml"))
        rmdir(self, join(self.source_folder, "include", "ogdf", "lib", "pugixml"))
        rmdir(self, join(self.source_folder, "include", "ogdf", "lib", "mapbox"))
        # do not set C++ standard
        replace_in_file(self, join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD ", "## set(CMAKE_CXX_STANDARD ")
        # use cci packages where available
        replace_in_file(self, join(self.source_folder, "CMakeLists.txt"), "include(coin)", "find_package(coin-clp REQUIRED CONFIG)\nfind_package(pugixml REQUIRED CONFIG)\nfind_package(earcut_hpp REQUIRED CONFIG)")
        replace_in_file(self, join(self.source_folder, "cmake", "ogdf.cmake"), "target_link_libraries(OGDF PUBLIC COIN)", "target_link_libraries(OGDF PUBLIC coin-clp::coin-clp pugixml::pugixml earcut_hpp::earcut_hpp)")
        # replace pugixml copy in repo by conan dependency
        for dir_name, file_name in [("include", "GexfParser.h"),
                                    ("include", "GraphMLParser.h"),
                                    ("include", "SvgPrinter.h"),
                                    ("include", "TsplibXmlParser.h"),
                                    ("src", "GraphIO_graphml.cpp"),
                                    ("src", "GraphIO_gexf.cpp"),
                                    ("src", "GexfParser.cpp"),
                                    ("src", "SvgPrinter.cpp"),
                                    ("src", "GraphMLParser.cpp"),
                                    ("src", "TsplibXmlParser.cpp")]:
            replace_in_file(self, join(self.source_folder, dir_name, "ogdf", "fileformats", file_name), "ogdf/lib/pugixml/pugixml.h", "pugixml.hpp")
        # replace earcut
        replace_in_file(self, join(self.source_folder, "include", "ogdf", "geometric", "cr_min", "geometry", "algorithm", "MapBoxTriangulation.h"), "ogdf/lib/mapbox/mapbox_earcut.h", "mapbox/mapbox_earcut.h")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="OGDF")

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, pattern="*.h", src=join(self.package_folder, "include", "ogdf-release", "ogdf"), dst=join(self.package_folder, "include", "ogdf"))
        rmdir(self, join(self.package_folder, "include", "ogdf-release"))
        copy(self, pattern="*.h", src=join(self.package_folder, "include", "ogdf-debug", "ogdf"), dst=join(self.package_folder, "include", "ogdf"))
        rmdir(self, join(self.package_folder, "include", "ogdf-debug"))

    def package_info(self):
        self.cpp_info.libs = ["OGDF"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
