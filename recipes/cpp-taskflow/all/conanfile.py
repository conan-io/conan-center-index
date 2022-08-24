import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.28.0"

class CppTaskflowConan(ConanFile):
    name = "cpp-taskflow"
    description = "A fast C++ header-only library to help you quickly write parallel programs with complex task dependencies."
    topics = ("conan", "cpp-taskflow", "taskflow", "tasking", "parallelism")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cpp-taskflow/cpp-taskflow"
    license = "MIT"
    no_copy_source = True
    settings = "os", "compiler"
    deprecated = "taskflow"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        compiler = str(self.settings.compiler)
        compiler_version = tools.Version(self.settings.compiler.version)
        min_req_cppstd = "17" if tools.Version(self.version) <= "2.2.0" else "14"

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, min_req_cppstd)
        else:
            self.output.warn("%s recipe lacks information about the %s compiler"
                             " standard version support" % (self.name, compiler))

        minimal_version = {
            "17": {
                "Visual Studio": "16",
                "gcc": "7.3",
                "clang": "6.0",
                "apple-clang": "10.0"
            },
            "14": {
                "Visual Studio": "15",
                "gcc": "5",
                "clang": "4.0",
                "apple-clang": "8.0"
            }
        }

        if compiler not in minimal_version[min_req_cppstd]:
            self.output.info("%s requires a compiler that supports at least C++%s" % (self.name, min_req_cppstd))
            return

        # Exclude compilers not supported by cpp-taskflow
        if compiler_version < minimal_version[min_req_cppstd][compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports"
                                            " at least C++%s. %s %s is not"
                                            " supported." % (self.name, min_req_cppstd, compiler, tools.Version(self.settings.compiler.version.value)))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("taskflow-" + self.version, self._source_subfolder)

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
