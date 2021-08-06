from conans import ConanFile, CMake, tools


class ArteryFontFormatConan(ConanFile):
    name = "artery-font-format"
    version = "1.0"
    license = "MIT"
    homepage = "https://github.com/Chlumsky/artery-font-format"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Artery Atlas Font format library"
    topics = ("conan", "artery", "font", "atlas")
    no_copy_source = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self.source_folder)
        tools.tools_files.rename("artery-font", "include/artery-font")

    def package(self):
        self.copy("*.h")
        self.copy("*.hpp")
        self.copy("LICENSE.txt", dst="licenses", src=self.source_folder)
