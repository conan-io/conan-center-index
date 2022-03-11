import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class StrawberryperlConan(ConanFile):
    name = "strawberryperl"
    description = "Strawbery Perl for Windows. Useful as build_require"
    license = "GNU Public License or the Artistic License"
    homepage = "http://strawberryperl.com"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "installer", "perl", "windows")
    settings = "os", "arch"
    short_paths = True

    def configure(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Only windows supported for Strawberry Perl.")

    def build(self):
        arch = str(self.settings.arch)
        url = self.conan_data["sources"][self.version]["url"][arch]
        sha256 = self.conan_data["sources"][self.version]["sha256"][arch]
        tools.get(url, sha256=sha256)

    def package(self):
        self.copy(pattern="License.rtf*", dst="licenses", src="licenses")
        self.copy(pattern="*", src=os.path.join("perl", "bin"), dst="bin")
        self.copy(pattern="*", src=os.path.join("perl", "lib"), dst="lib")
        self.copy(pattern="*", src=os.path.join("perl", "vendor", "lib"), dst="lib")
        self.copy(pattern="*", src=os.path.join("c", "bin"), dst="bin")
        self.copy(pattern="*", src=os.path.join("c", "lib"), dst="lib")
        self.copy(pattern="*", src=os.path.join("c", "include"), dst="include")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: %s" % bin_path)
        self.env_info.PATH.append(bin_path)

        self.user_info.perl = os.path.join(self.package_folder, "bin", "perl.exe").replace("\\", "/")
