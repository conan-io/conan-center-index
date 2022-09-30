from conan import ConanFile
from conans import tools
from conans.errors import ConanInvalidConfiguration


required_conan_version = ">=1.43.0"


class TllistConan(ConanFile):
    name = "tllist"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://codeberg.org/dnkl/tllist"
    description = "A C header file only implementation of a typed linked list."
    topics = ("list", "utils", "typed-linked-list")
    settings = "os", "arch", "build_type", "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        # tllist relies on __typeof__, not implemented in Visual Studio
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio compiler is not supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", src=self._source_subfolder, dst="include")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "tllist")
