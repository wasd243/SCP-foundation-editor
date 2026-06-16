# syntax=docker/dockerfile:1
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    CARGO_HOME=/usr/local/cargo \
    RUSTUP_HOME=/usr/local/rustup \
    PATH=/usr/local/cargo/bin:$PATH

# OS
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl git file build-essential pkg-config \
        libssl-dev libglib2.0-dev libgtk-3-dev \
        libwebkit2gtk-4.1-dev libsoup-3.0-dev \
        libjavascriptcoregtk-4.1-dev libayatana-appindicator3-dev \
        librsvg2-dev libxdo-dev patchelf xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Node 22 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Rust stable + Tauri CLI
RUN curl --proto '=https' --tlsv1.2 -fsSL https://sh.rustup.rs \
        | sh -s -- -y --default-toolchain stable --profile minimal \
    && rustc --version && cargo --version
RUN cargo install tauri-cli --version "^2" --locked

WORKDIR /app

CMD ["bash"]
