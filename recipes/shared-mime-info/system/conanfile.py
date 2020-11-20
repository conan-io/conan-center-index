from conans import ConanFile, tools

class ConanSharedMimeInfo(ConanFile):
    name = "shared-mime-info"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPLv2"
    homepage = "https://freedesktop.org/wiki/Software/shared-mime-info/"
    description = "The shared-mime-info package contains the core database of common types and the update-mime-database command used to extend it."
    settings = {"os": "Linux"}
    topics = ("conan", "shared-mime-info")

    def package_id(self):
        self.info.header_only()

    def system_requirements(self):
        if tools.os_info.is_linux and self.settings.os == "Linux":
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode="verify")
            package_tool.install(update=True, packages=["shared-mime-info"])
