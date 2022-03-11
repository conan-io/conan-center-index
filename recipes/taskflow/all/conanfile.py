import os

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"

class TaskflowConan(ConanFile):
    name = "taskflow"
    description = "A fast C++ header-only library to help you quickly write parallel programs with complex task dependencies."
    topics = ("taskflow", "tasking", "parallelism")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taskflow/taskflow"
    license = "MIT"

    settings = "os", "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def validate(self):
        minimal_cpp_standard = "17" if tools.Version(self.version) <= "2.2.0" or tools.Version(self.version) >= "3.0.0"  else "14"

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

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
        }[minimal_cpp_standard]

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
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            print(patch)
            tools.patch(**patch)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst=os.path.join("include", "taskflow"), src=os.path.join(self._source_subfolder, "taskflow"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.defines.append("_ENABLE_EXTENDED_ALIGNED_STORAGE")
        self.cpp_info.names["cmake_find_package"] = "Taskflow"
        self.cpp_info.names["cmake_find_package_multi"] = "Taskflow"
        self.cpp_info.set_property("cmake_target_name", "Taskflow::Taskflow")
