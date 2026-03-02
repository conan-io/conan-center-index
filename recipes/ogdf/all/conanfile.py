from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir, rm
from conan.errors import ConanInvalidConfiguration
from os.path import join

required_conan_version = ">=2.1"


class OGDFConan(ConanFile):
    name = "ogdf"
    description = "Open Graph algorithms and Data structures Framework"
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ogdf.net"
    topics = ("graph", "algorithm", "data-structures")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def validate(self):
        check_min_cppstd(self, 17)
        if cross_building(self) and is_apple_os(self):
            # FIXME: https://github.com/ogdf/ogdf/issues/214
            # error: unknown target CPU 'apple-m2'
            raise ConanInvalidConfiguration("Cross-building is not support on Mac yet. See https://github.com/ogdf/ogdf/issues/214.")

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
        self.requires("pugixml/[>=1.14 <2]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["COIN_SOLVER"] = "CLP"
        tc.cache_variables["COIN_SOLVER_IS_EXTERNAL"] = 0
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        # delete code from other cci packages
        rmdir(self, join(self.source_folder, "src", "coin"))
        rmdir(self, join(self.source_folder, "include", "coin"))
        rmdir(self, join(self.source_folder, "include", "ogdf", "lib", "backward"))
        # do not set C++ standard
        replace_in_file(self, join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD ", "## set(CMAKE_CXX_STANDARD ")
        # use cci packages where available
        replace_in_file(self, join(self.source_folder, "CMakeLists.txt"), "include(coin)", "find_package(coin-clp REQUIRED CONFIG)\nfind_package(pugixml REQUIRED CONFIG)")
        replace_in_file(self, join(self.source_folder, "cmake", "ogdf.cmake"), "target_link_libraries(OGDF PUBLIC COIN)", "target_link_libraries(OGDF PUBLIC coin-clp::coin-clp pugixml::pugixml)")
        # replace pugixml copy in repo by conan dependency
        rmdir(self, join(self.source_folder, "src", "ogdf", "lib", "pugixml"))
        rmdir(self, join(self.source_folder, "include", "ogdf", "lib", "pugixml"))
        for dir_name, file_name in [("include", "GexfParser.h"),
                                    ("include", "GraphMLParser.h"),
                                    ("include", "SvgPrinter.h"),
                                    ("include", "TsplibXmlParser.h"),
                                    ("src", "GexfParser.cpp"),
                                    ("src", "GraphMLParser.cpp"),
                                    ("src", "SvgPrinter.cpp"),
                                    ("src", "TsplibXmlParser.cpp"),
                                    ("src", "GraphIO_graphml.cpp"),
                                    ("src", "GraphIO_gexf.cpp")]:
            replace_in_file(self, join(self.source_folder, dir_name, "ogdf", "fileformats", file_name), "ogdf/lib/pugixml/pugixml.h", "pugixml.hpp")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="OGDF")

    def package(self):
        copy(self, pattern="LICENSE*", src=self.source_folder, dst=join(self.package_folder, "licenses"))
        copy(self, pattern="LICENSE*", src=join(self.source_folder, "include", "ogdf", "lib", "minisat"), dst=join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        copy(self, pattern="*.h", src=join(self.package_folder, "include", "ogdf-release", "ogdf"), dst=join(self.package_folder, "include", "ogdf"))
        rmdir(self, join(self.package_folder, "include", "ogdf-release"))
        copy(self, pattern="*.h", src=join(self.package_folder, "include", "ogdf-debug", "ogdf"), dst=join(self.package_folder, "include", "ogdf"))
        rmdir(self, join(self.package_folder, "include", "ogdf-debug"))
        rmdir(self, join(self.package_folder, "lib", "cmake"))
        rmdir(self, join(self.package_folder, "share"))
        for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
            rm(self, dll_pattern_to_remove, join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["OGDF"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
