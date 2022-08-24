from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class NumCppConan(ConanFile):
    name = "numcpp"
    description = "A Templatized Header Only C++ Implementation of the Python NumPy Library"
    topics = ("python", "numpy", "numeric")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dpilger26/NumCpp"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_boost" : [True, False],
        "threads" : [True, False],
    }
    default_options = {
        "with_boost" : True,
        "threads" : False,
    }

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if tools.Version(self.version) < "2.5.0":
            del self.options.with_boost
            self.options.threads = True

    def requirements(self):
        if tools.Version(self.version) < "2.5.0" or self.options.with_boost:
            self.requires("boost/1.78.0")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "14"
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return
        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "NumCpp")
        self.cpp_info.set_property("cmake_target_name", "NumCpp::NumCpp")
        if not self.options.get_safe("with_boost", False):
            self.cpp_info.defines.append("NUMCPP_NO_USE_BOOST")

        if tools.Version(self.version) < "2.5.0" and not self.options.threads:
            self.cpp_info.defines.append("NO_MULTITHREAD")
        if tools.Version(self.version) >= "2.5.0" and self.options.threads:
            self.cpp_info.defines.append("NUMCPP_USE_MULTITHREAD")

        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "NumCpp"
        self.cpp_info.names["cmake_find_package_multi"] = "NumCpp"
