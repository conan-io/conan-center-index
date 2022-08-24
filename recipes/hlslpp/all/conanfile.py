from conan import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class HlslppConan(ConanFile):
    name = "hlslpp"
    description = "Header-only Math library using hlsl syntax with SSE/NEON support"
    topics = ("conan", "hlslpp", "hlsl", "math", "shader", "vector", "matrix", "quaternion")
    license = "MIT"
    homepage = "https://github.com/redorav/hlslpp"
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
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
