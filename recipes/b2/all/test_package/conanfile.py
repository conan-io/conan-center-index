from conans import ConanFile, tools
import os


class TestPackgeConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        tools.save(
            "jamroot.jam",
            'ECHO "info:" Success loading project jamroot.jam file. ;')
        tools.save(
            "boost-build.jam",
            "boost-build \"" +
            os.environ['BOOST_BUILD_PATH'].replace("\\", "/")+"\" ;"
        )
        self.run("b2 --debug-configuration")
