from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc
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

    def validate(self):
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

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
        self.requires("pugixml/1.13")

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
        # use cci packages where available
        replace_in_file(self, join(self.source_folder, "CMakeLists.txt"), "include(coin)", "find_package(coin-clp REQUIRED CONFIG)\nfind_package(pugixml REQUIRED CONFIG)")
        replace_in_file(self, join(self.source_folder, "cmake", "ogdf.cmake"), "target_link_libraries(OGDF PUBLIC COIN)", "target_link_libraries(OGDF PUBLIC coin-clp::coin-clp pugixml::pugixml)")
        # replace pugixml copy in repo by conan dependency
        for dir_name, file_name in [("include", "GexfParser.h"),
                                    ("include", "GraphMLParser.h"),
                                    ("include", "SvgPrinter.h"),
                                    ("include", "TsplibXmlParser.h"),
                                    ("src", "GraphIO_graphml.cpp"),
                                    ("src", "GraphIO_gexf.cpp")]:
            replace_in_file(self, join(self.source_folder, dir_name, "ogdf", "fileformats", file_name), "ogdf/lib/pugixml/pugixml.h", "pugixml.hpp")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="OGDF")

    def package(self):
        copy(self, pattern="LICENSE*.txt", src=self.source_folder, dst=join(self.package_folder, "licenses"))
        copy(self, pattern="*.h", src=join(self.source_folder, "include"), dst=join(self.package_folder, "include"))
        copy(self, pattern="*.h", src=join(self.build_folder, "include"), dst=join(self.package_folder, "include"))
        if self.options.shared:
            copy(self, pattern="*.so*", src=self.build_folder, dst=join(self.package_folder, "lib"))
            copy(self, pattern="*.dylib*", src=self.build_folder, dst=join(self.package_folder, "lib"))
        else:
            copy(self, pattern="*.a", src=self.build_folder, dst=join(self.package_folder, "lib"))
            copy(self, pattern="*.lib", src=self.build_folder, dst=join(self.package_folder, "lib"), keep_path=False)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["OGDF"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
