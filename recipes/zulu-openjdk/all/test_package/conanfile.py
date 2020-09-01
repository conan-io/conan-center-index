from conans import ConanFile
import subprocess

class TestPackage(ConanFile):

    def test(self):
        output = subprocess.run(['java', '--version'], stdout=subprocess.PIPE)
        version_info = output.stdout.decode('utf-8')
        if "Zulu" in version_info:
            pass
        else:
            raise Exception("java call seems not use the Zulu bin")
