from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version



class ConfuJson(ConanFile):
    name = "confu_json"
    homepage = "https://github.com/werto87/confu_json"
    description = "uses boost::fusion to help with serialization; json <-> user defined type"
    topics = ("json parse", "serialization", "user defined type")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 20

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "17",
            "gcc": "10",
            "clang": "10",
        }


       
    def configure(self):
        if is_msvc(self) and Version(self.version) < "0.0.10":
            raise ConanInvalidConfiguration(
                "Visual Studio is not supported in versions before confu_json/0.0.10")
        if self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration(
                "apple-clang is not supported because of missing concept support")
        if self.settings.compiler.get_safe("cppstd"):
         tools.build.check_min_cppstd(self, self._minimum_cpp_standard)

        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} "
                             "compiler support.".format(
                                 self.name, self.settings.compiler))
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++{} support. "
                    "The current compiler {} {} does not support it.".format(
                        self.name, self._minimum_cpp_standard,
                        self.settings.compiler,
                        self.settings.compiler.version))
        self.options["boost"].header_only = True

    def requirements(self):
        self.requires("boost/1.79.0")
        self.requires("magic_enum/0.8.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
        destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*.h*", dst="include/confu_json",
                  src="source_subfolder/confu_json")
        self.copy("*LICENSE.md", dst="licenses", keep_path=False)

    def package_id(self):
        self.info.header_only()
