from conans import ConanFile
import os


class TestPackageConan(ConanFile):

    def build(self):
        test_file = os.path.join(self.source_folder, "test_package.m4")
        in_file = os.path.join(self.build_folder, "input.m4")
        with open(in_file, "wb") as f_in_file, open(test_file, "rb") as f_test_file:
            f_in_file.write(f_test_file.read().replace(b"\r\n", b"\n"))
        assert "\r\n" not in open(in_file, "r")

        self.run("{} --version".format(os.environ["M4"]))
        self.run("{} -P {}".format(os.environ["M4"], in_file))
        self.run("{} -P {} > out".format(os.environ["M4"], in_file))

    def test(self):
        if b"\r\n" in open("out", "rb"):
            raise Exception("m4 output has DOS line-endings!")
