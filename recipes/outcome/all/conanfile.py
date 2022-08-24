import os
from conans import ConanFile, errors, tools

class OutcomeConan(ConanFile):
    name = "outcome"
    homepage = "https://github.com/ned14/outcome"
    description = "Provides very lightweight outcome<T> and result<T>"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("outcome", "result")
    settings = "compiler"
    no_copy_source = True

    _source_subfolder = "source_subfolder"

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "14")

        minimum_version = {
            "clang": "3.9",
            "gcc": "6",
            "Visual Studio": "15.0",
        }.get(str(self.settings.compiler))

        if not minimum_version:
            self.output.warn(
                "Unknown compiler {} {}. Assuming compiler supports C++14."
                .format(self.settings.compiler, self.settings.compiler.version))
        else:
            version = tools.Version(self.settings.compiler.version)
            if version < minimum_version:
                raise errors.ConanInvalidConfiguration(
                    "The compiler {} {} does not support C++14."
                    .format(self.settings.compiler, self.settings.compiler.version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("outcome.hpp", dst="include",
                src=os.path.join(self._source_subfolder, "single-header"))
        self.copy("Licence.txt", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
