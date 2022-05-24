import os

from conans import ConanFile, tools


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

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "fpgen"))
