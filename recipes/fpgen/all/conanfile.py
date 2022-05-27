import os

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class FpgenConan(ConanFile):
    name = "fpgen"
    description = " Functional programming in C++ using C++20 coroutines."
    license = ["MPL2"]
    topics = (
        "generators",
        "coroutines",
        "c++20",
        "header-only",
        "functional-programming",
        "functional",
    )
    homepage = "https://github.com/jay-tux/fpgen/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        print(os.listdir(self.name + "-" + self.version))
        bpth = self.name + "-" + self.version
        os.rename(bpth + "/LICENSE", bpth + "/inc/LICENSE")
        os.rename(bpth + "/inc/", self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(
            pattern="*.hpp",
            dst=os.path.join("include", "fpgen"),
            src=self._source_subfolder,
        )

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 20)
        else:
            self.output.warn("Could not check availability of C++20.")

        if not str(self.settings.compiler) == 'gcc':
            raise ConanInvalidConfiguration("{} is currently only available for GCC 10+. We're working on support for other compilers...".format(self.name))
        elif tools.Version(self.settings.compiler.version) < "10":
            raise ConanInvalidConfiguration("{} requires C++20 coroutines. Please use GCC 10 or newer.".format(self.name))

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "fpgen"))
