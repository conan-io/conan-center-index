from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.43.0"

class TaskflowConan(ConanFile):
    name = "taskflow"
    description = (
        "A fast C++ header-only library to help you quickly write parallel "
        "programs with complex task dependencies."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taskflow/taskflow"
    topics = ("taskflow", "tasking", "parallelism")
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _min_cppstd(self):
        if tools.Version(self.version) >= "3.0.0":
            return "17"
        return "14"

    @property
    def _minimum_compiler_version(self):
        return {
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
            },
        }[self._min_cppstd]

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)

        min_version = self._minimum_compiler_version.get(str(self.settings.compiler))
        if min_version and tools.Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(
                "{} requires a compiler that supports at least C++{}".format(
                    self.name, self._min_cppstd,
                )
            )

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*",
                  dst=os.path.join("include", "taskflow"),
                  src=os.path.join(self._source_subfolder, "taskflow"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Taskflow")
        self.cpp_info.set_property("cmake_target_name", "Taskflow::Taskflow")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        if is_msvc(self):
            self.cpp_info.defines.append("_ENABLE_EXTENDED_ALIGNED_STORAGE")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Taskflow"
        self.cpp_info.names["cmake_find_package_multi"] = "Taskflow"
