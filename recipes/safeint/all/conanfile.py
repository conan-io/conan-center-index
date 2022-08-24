from conan import ConanFile, tools$

required_conan_version = ">=1.33.0"


class SafeintConan(ConanFile):
    name = "safeint"
    description = "SafeInt is a class library for C++ that manages integer overflows."
    license = "MIT"
    topics = ("conan", "safeint", "integer", "overflow")
    homepage = "https://github.com/dcleblanc/SafeInt"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("SafeInt.hpp", dst="include", src=self._source_subfolder)
