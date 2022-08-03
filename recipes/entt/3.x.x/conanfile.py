from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.47.0"


class EnttConan(ConanFile):
    name = "entt"
    description = "Gaming meets modern C++ - a fast and reliable entity-component system (ECS) and much more"
    topics = ("entt", "gaming", "entity", "ecs")
    homepage = "https://github.com/skypjack/entt"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def validate(self):
        minimal_cpp_standard = "17"
        if self.settings.compiler.get_safe("cppstd"):
            tools_legacy.check_min_cppstd(self, minimal_cpp_standard)

        minimal_version = {
            "Visual Studio": "15.9",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10"
        }

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return

        # Compare versions asuming minor satisfies if not explicitly set
        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        if lazy_lt_semver(str(self.settings.compiler.version), minimal_version[compiler]):
            raise ConanInvalidConfiguration(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", src=os.path.join(self.source_folder, self._source_subfolder),
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*", src=os.path.join(self.source_folder, self._source_subfolder, "src"),
             dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "EnTT")
        self.cpp_info.set_property("cmake_target_name", "EnTT::EnTT")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.names["cmake_find_package"] = "EnTT"
        self.cpp_info.names["cmake_find_package_multi"] = "EnTT"
