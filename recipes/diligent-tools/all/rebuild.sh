conan source  . --source-folder=sources && \
conan install . --install-folder=build --build missing && \
conan build   . --build-folder=build && \
conan package . --build-folder=build --package-folder=bin
