from conan import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class MaddyConan(ConanFile):
    name = "maddy"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/progsource/maddy"
    description = (
        "open-source, maddy is a C++ Markdown to HTML header-only parser library."
    )
    topics = ("maddy", "markdown", "header-only")
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 14)

    def source(self):
        tools.files.get(self, 
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            strip_root=True
        )

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy(
            "LICENSE",
            src=os.path.join(self.source_folder, self._source_subfolder),
            dst="licenses",
        )
        self.copy(
            pattern="maddy/*.h",
            src=os.path.join(self.source_folder, self._source_subfolder, "include"),
            dst="include",
        )
