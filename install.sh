#!/bin/bash


# Installing requirements
pip install -r requirements.txt


if lspci | grep -iq "nvidia"; then
  echo "NVidia GPU is available, installing with CUDA support"
  CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install --no-cache-dir llama-cpp-python==0.2.90 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124 --upgrade --force-reinstall
else
  echo "NVidia GPU is not available, installing with OpenBLAS support"
  CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS -DLLAVA_BUILD=OFF" pip install llama-cpp-python==0.2.90 --upgrade --force-reinstall
fi

