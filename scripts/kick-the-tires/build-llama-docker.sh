#!/bin/bash
set -e

SHARE_DIR=/home/vectorxj/share

chcore_upload() {
    APP_DIR=/home/vectorxj/openharmony/base/tee/tee_os_kernel/oh_tee/apps

    cp ggml/src/libggml.so $APP_DIR/
    cp src/libllama.so $APP_DIR/
    cp bin/llama-cli $APP_DIR/
}

rknpure_upload() {
    mkdir -p $SHARE_DIR/build-rknpure
    BUILD_RKNPURE_DIR=$SHARE_DIR/build-rknpure
    cp ggml/src/libggml.so $BUILD_RKNPURE_DIR/
    cp src/libllama.so $BUILD_RKNPURE_DIR/
    cp src/libremoting_backend.so $BUILD_RKNPURE_DIR/
    cp bin/llama-cli $BUILD_RKNPURE_DIR/
    # cp bin/ca $BUILD_RKNPURE_DIR/
    cp bin/fake $BUILD_RKNPURE_DIR/

    # hdc file send ggml/src/libggml.so /data/local/tmp/rknpu
    # hdc file send src/libllama.so /data/local/tmp/rknpu
    # hdc file send src/libremoting_backend.so /data/local/tmp/rknpu
    # hdc file send bin/llama-cli /data/local/tmp/rknpu
    # # hdc file send bin/ca /data/local/tmp/rknpu
    # hdc file send bin/fake /data/local/tmp/rknpu
}

cd /home/vectorxj/chcore/opentrustee_llm/llama.cpp

if [ ! -d build-chcore ]; then
    mkdir -p build-chcore
    pushd build-chcore
    cmake -DCMAKE_TOOLCHAIN_FILE=/home/vectorxj/chcore/staros/build/toolchain.cmake -DGGML_NATIVE=OFF -DGGML_OPENMP=OFF -DLLAMA_BUILD_TESTS=OFF -DGGML_RKNPU2=OFF -DGGML_RKNPURE=ON ..
    popd
fi

pushd build-chcore
make -j$(nproc)
chcore_upload
popd

if [ ! -d build-rknpure ]; then
    mkdir -p build-rknpure
    cmake -DCMAKE_C_COMPILER=/usr/bin/aarch64-linux-gnu-gcc -DCMAKE_CXX_COMPILER=/usr/bin/aarch64-linux-gnu-g++ -DGGML_NATIVE=OFF -DGGML_OPENMP=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_CHCORE_API=OFF -DGGML_CHCORE=OFF -B build-rknpure
fi

pushd build-rknpure
make -j$(nproc)
rknpure_upload
popd
