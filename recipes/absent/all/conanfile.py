from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os.path


class AbsentConan(ConanFile):
    name = "absent"
    description = "A simple library to compose nullable types in a generic, type-safe, and declarative style for C++"
    homepage = "https://github.com/rvarago/absent"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    author = "Rafael Varago (rvarago)"
    topics = ("nullable-types", "composition", "monadic-interface", "declarative-programming")
    no_copy_source = True
    settings = "compiler"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"
    
    def supports_cpp17(self):
        supported_compilers = [("gcc", "7"), ("clang", "5"), ("apple-clang", "10"), ("Visual Studio", "15.7")]
        compiler = self.settings.compiler
        version = Version(self.settings.compiler.version)
        return any(compiler == e[0] and version >= e[1] for e in supported_compilers)
            
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.configure(source_folder=self._source_subfolder,
                        build_folder=self._build_subfolder)
        return cmake

    def configure(self):
        version = Version(self.settings.compiler.version)
        compiler = self.settings.compiler
        if not self.supports_cpp17():
            raise ConanInvalidConfiguration("Absent requires C++17 support")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_id(self):
        self.info.header_only()
