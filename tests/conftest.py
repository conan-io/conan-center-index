import pytest


def pytest_addoption(parser):
    parser.addoption('--upload-to', help='upload built packages to the given remote')
    parser.addoption('--force-build', choices=['package', 'with-requirements'], const='package', nargs='?',
                     help='Force a build of the package or the package with its requirements')


@pytest.fixture(scope='package')
def upload_to(request):
    return request.config.getoption('--upload-to')


@pytest.fixture
def force_build(request):
    return request.config.getoption('--force-build')
