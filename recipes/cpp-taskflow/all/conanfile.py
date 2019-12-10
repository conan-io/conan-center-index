from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.model.version import Version
import os


class CppTaskflowConan(ConanFile):
    name = "cpp-taskflow"
    version = "2.2.0"
    description = "A fast C++ header-only library to help you quickly write parallel programs with complex task dependencies."
    topics = ("conan", "cpp-taskflow", "tasking", "parallelism")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cpp-taskflow/cpp-taskflow"
    license = "MIT"

    no_copy_source = True

    settings = "os", "compiler"
    
    _source_subfolder = "source_subfolder"
    
    def configure(self):
        tools.check_min_cppstd(self, "17")

        compiler = self.settings.compiler
        compiler_version = Version(self.settings.compiler.version.value)
        # Exclude compilers not supported by cpp-taskflow
        if (compiler == "gcc" and compiler_version < "7.3") or \
           (compiler == "clang" and compiler_version < "6") or \
           (compiler == "apple-clang" and compiler_version < "10.0") or \
           (compiler == "Visual Studio" and compiler_version < "16"):
          raise ConanInvalidConfiguration("cpp-taskflow requires C++17 standard or higher. {} {} is not supported.".format(compiler, compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include/taskflow", src=os.path.join(self._source_subfolder, "taskflow"))
    
    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        
