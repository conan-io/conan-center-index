from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.2 <1.51.0 || >=1.51.2"


class LibrttopoConan(ConanFile):
    name = "librttopo"
    description = (
        "The RT Topology Library exposes an API to create and manage "
        "standard (ISO 13249 aka SQL/MM) topologies."
    )
    license = "GPL-2.0-or-later"
    topics = ("librttopo", "topology", "geospatial", "gis")
    homepage = "https://git.osgeo.org/gitea/rttopo/librttopo"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def requirements(self):
        self.requires("geos/3.11.0")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBRTTOPO_SRC_DIR"] = self.source_folder.replace("\\", "/")
        librttopo_version = Version(self.version)
        tc.variables["LIBRTGEOM_VERSION_MAJOR"] = librttopo_version.major
        tc.variables["LIBRTGEOM_VERSION_MINOR"] = librttopo_version.minor
        tc.variables["LIBRTGEOM_VERSION_PATCH"] = librttopo_version.patch
        geos_version = Version(self.dependencies["geos"].ref.version)
        tc.variables["RTGEOM_GEOS_VERSION"] = f"{geos_version.major}{geos_version.minor}"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "rttopo")
        self.cpp_info.libs = ["rttopo"]
        self.cpp_info.requires = ["geos::geos_c"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
