script_folder="/home/mg/andi/mgconsole-conan/all/test_package"
echo "echo Restoring environment" > "$script_folder/deactivate_conanrunenv-relwithdebinfo-x86_64.sh"
for v in PATH
do
    is_defined="true"
    value=$(printenv $v) || is_defined="" || true
    if [ -n "$value" ] || [ -n "$is_defined" ]
    then
        echo export "$v='$value'" >> "$script_folder/deactivate_conanrunenv-relwithdebinfo-x86_64.sh"
    else
        echo unset $v >> "$script_folder/deactivate_conanrunenv-relwithdebinfo-x86_64.sh"
    fi
done


export PATH="/home/mg/.conan2/p/b/mgconfa812209655b0/p/bin:$PATH"