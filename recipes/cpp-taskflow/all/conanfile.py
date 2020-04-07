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
        compiler = str(self.settings.compiler)
        compiler_version = tools.Version(self.settings.compiler.version)

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "17")
        else:
            self.output.warn("%s recipe lacks information about the %s compiler"
                             " standard version support" % (self.name, compiler))
        
        minimal_version = {
            "Visual Studio": "16",
            "gcc": "7.3",
            "clang": "6",
            "apple-clang": "10.0"
        }

        if compiler not in minimal_version:            
            self.output.info("%s requires a compiler that supports at least"
                             " C++17" % self.name)
            return
        
        # Exclude compilers not supported by cpp-taskflow
        if compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports"
                                            " at least C++17. %s %s is not" 
                                            " supported." % (self.name, compiler, Version(self.settings.compiler.version.value)))

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
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.defines.append("_ENABLE_EXTENDED_ALIGNED_STORAGE")
        
