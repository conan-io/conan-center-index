from conan import ConanFile, tools$
import os


class MapboxGeometryConan(ConanFile):
    name = "mapbox-geometry"
    description = (
        "Provides header-only, generic C++ interfaces for geometry types, "
        "geometry collections, and features."
    )
    topics = ("geometry")
    license = "ISC"
    homepage = "https://github.com/mapbox/geometry.hpp"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("mapbox-variant/1.2.0")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 14)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))
