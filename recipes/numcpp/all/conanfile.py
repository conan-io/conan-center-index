from conans import ConanFile, tools
import os
import glob
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.32.0"

class NumCppConan(ConanFile):
    name = "numcpp"
    description = "A Templatized Header Only C++ Implementation of the Python NumPy Library"
    topics = ("python", "numpy", "numeric")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dpilger26/NumCpp"
    options = {
        "with_boost" : [True, False],
        "threads" : [True, False],
    }
    default_options = {
        "with_boost" : True,
        "threads" : False,
    }
    license = "MIT"
    no_copy_source = True
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
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

    def requirements(self):
        if tools.Version(self.version) < "2.5.0" or self.options.with_boost:
            self.requires("boost/1.75.0")

    def config_options(self):
        if tools.Version(self.version) < "2.5.0":
            del self.options.with_boost
            self.options.threads = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("NumCpp-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
        
    def package_info(self):
        if not self.options.get_safe("with_boost", False):
            self.cpp_info.cxxflags.append("-DNUMCPP_NO_USE_BOOST")

        if tools.Version(self.version) < "2.5.0" and self.options.threads == False:
            self.cpp_info.defines.append("NO_MULTITHREAD")
        if tools.Version(self.version) >= "2.5.0" and self.options.threads == True:
            self.cpp_info.defines.append("NUMCPP_USE_MULTITHREAD")

        self.cpp_info.names["cmake_find_package"] = "NumCpp"
        self.cpp_info.names["cmake_find_package_multi"] = "NumCpp"
