from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class CppTaskflowConan(ConanFile):
    name = "cpp-taskflow"
    version = "2.2.0"
    description = "A fast C++ header-only library to help you quickly write parallel programs with complex task dependencies."
    topics = ("conan", "cpp-taskflow", "tasking", "parallelism")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cpp-taskflow/cpp-taskflow"
    author = "Hopobcn <hopobcn@gmail.com>"
    license = "MIT"

    no_copy_source = True

    settings = "os", "compiler"
    
    _source_subfolder = "source_subfolder"
    
    def configure(self):    
        if not self.settings.compiler.cppstd:
            self.settings.compiler.cppstd = 17
        elif self.settings.compiler.cppstd.value < "17":
            raise ConanInvalidConfiguration("cpp-taskflow requires c++17")
    
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
            self.cpp_info.libs.append("pthread")
        
