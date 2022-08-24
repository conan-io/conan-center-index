from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

class DecoConan(ConanFile):
    name = "deco"
    license = "Apache-2.0-WITH-LLVM-exception"
    description = "Delimiter Collision Free Format"
    topics = ("serialization")
    homepage = "https://github.com/Enhex/Deco"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    settings = ("compiler", "build_type", "os", "arch")
    requires = (
        "enhex-generic_serialization/1.0.0",
        "enhex-strong_type/1.0.0",
        "boost/1.79.0",
        "rang/3.2",
    )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)

        minimal_version = {
            "Visual Studio": "15",
            "gcc": "7",
            "clang": "5.0",
            "apple-clang": "9.1"
        }
        compiler = str(self.settings.compiler)
        compiler_version = tools.Version(self.settings.compiler.version)

        if compiler not in minimal_version:
            self.output.info("{} requires a compiler that supports at least C++17".format(self.name))
            return

        # Exclude compilers not supported
        if compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("{} requires a compiler that supports at least C++17. {} {} is not".format(
                self.name, compiler, tools.Version(self.settings.compiler.version.value)))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()
