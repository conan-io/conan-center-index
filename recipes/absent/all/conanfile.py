from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os.path


class AbsentConan(ConanFile):
    name = "absent"
    description = "A small library meant to simplify the composition of nullable types in a generic, type-safe, and declarative style for some C++ type-constructors"
    homepage = "https://github.com/rvarago/absent"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    topics = ("nullable-types", "composition", "monadic-interface", "declarative-programming")
    no_copy_source = True
    settings = "compiler"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _supports_cpp17(self):
        supported_compilers = [("gcc", "7"), ("clang", "5"), ("apple-clang", "10"), ("Visual Studio", "15.7")]
        compiler = self.settings.compiler
        version = Version(compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)
            
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        elif not self._supports_cpp17():
            raise ConanInvalidConfiguration("Absent requires C++17 support")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_id(self):
        self.info.header_only()
