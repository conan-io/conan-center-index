import os

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class EnttConan(ConanFile):
    name = "entt"
    description = "Gaming meets modern C++ - a fast and reliable entity-component system (ECS) and much more"
    topics = ("conan", "entt", "gaming", "entity", "ecs")
    homepage = "https://github.com/skypjack/entt"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    no_copy_source = True
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        minimal_cpp_standard = "17"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

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

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "src"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "EnTT"
        self.cpp_info.names["cmake_find_package_multi"] = "EnTT"
