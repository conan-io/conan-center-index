from conans import ConanFile, CMake, tools
import functools

required_conan_version = ">=1.36.0"


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
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("geos/3.10.2")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        librttopo_version = tools.Version(self.version)
        cmake.definitions["LIBRTGEOM_VERSION_MAJOR"] = librttopo_version.major
        cmake.definitions["LIBRTGEOM_VERSION_MINOR"] = librttopo_version.minor
        cmake.definitions["LIBRTGEOM_VERSION_PATCH"] = librttopo_version.patch
        geos_version = tools.Version(self.deps_cpp_info["geos"].version)
        cmake.definitions["RTGEOM_GEOS_VERSION"] = "{}{}".format(geos_version.major, geos_version.minor)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "rttopo")
        self.cpp_info.libs = ["rttopo"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "rttopo"
