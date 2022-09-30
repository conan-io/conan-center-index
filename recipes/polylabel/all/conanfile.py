from conans import ConanFile, tools
import os


class PolylabelConan(ConanFile):
    name = "polylabel"
    description = "A fast algorithm for finding the pole of inaccessibility of a polygon."
    topics = ("polygon", "pole-of-inaccessibility")
    license = "ISC"
    homepage = "https://github.com/mapbox/polylabel"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("mapbox-geometry/2.0.3")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))
