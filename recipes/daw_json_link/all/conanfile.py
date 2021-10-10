from conans.errors import ConanInvalidConfiguration
from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"

class DawJsonLinkConan(ConanFile):
    name = "daw_json_link"
    description = "Static JSON parsing in C++ "
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/beached/daw_json_link"
    topics = ("json", "parse", "json-parser", "serialization", "constexpr", "header-only")
    settings = "os", "compiler"
    no_copy_source = True

    _compiler_required_cpp17 = {
        "Visual Studio": "16",
        "gcc": "7",
        "clang": "6",
        "apple-clang": "10",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "17")

        minimum_version = self._compiler_required_cpp17.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{0} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def package(self):
        licenses = ["LICENSE", "LICENSE_Dragonbox"]
        for license_file in licenses:
            self.copy(license_file, dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        tools.remove_files_by_mask(self.package_folder, "*.cmake")
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()
