echo Capturing current environment in "/Users/fernando/dev/conan-center-index/recipes/cppfront/all/test_package/build-release/conan/deactivate_conanrunenv-release-x86_64.sh"
echo "echo Restoring environment" >> "/Users/fernando/dev/conan-center-index/recipes/cppfront/all/test_package/build-release/conan/deactivate_conanrunenv-release-x86_64.sh"
for v in 
do
    is_defined="true"
    value=$(printenv $v) || is_defined="" || true
    if [ -n "$value" ] || [ -n "$is_defined" ]
    then
        echo export "$v='$value'" >> "/Users/fernando/dev/conan-center-index/recipes/cppfront/all/test_package/build-release/conan/deactivate_conanrunenv-release-x86_64.sh"
    else
        echo unset $v >> "/Users/fernando/dev/conan-center-index/recipes/cppfront/all/test_package/build-release/conan/deactivate_conanrunenv-release-x86_64.sh"
    fi
done

echo Configuring environment variables
