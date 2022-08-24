from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"

class GcemConan(ConanFile):
    name = "gcem"
    description = "A C++ compile-time math library using generalized " \
                  "constant expressions."
    license = "Apache-2.0"
    topics = ("gcem", "math", "header-only")
    homepage = "https://github.com/kthohr/gcem"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type",

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="*", dst="include",
                  src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
