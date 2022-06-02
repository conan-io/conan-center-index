#!/bin/bash

echo "Configuring CMake..."
cmake --preset=dev >/dev/null && \
echo "Done" && \
fd | entr -cc ./scripts/run.sh
