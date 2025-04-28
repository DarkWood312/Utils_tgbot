FROM python:3.12-slim

# Install system dependencies and tools needed to compile Rust and Binwalk
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libffi-dev \
    python3-dev \
    libfontconfig1-dev \
    liblzma-dev \
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Clone Binwalk repository
RUN git clone https://github.com/ReFirmLabs/binwalk.git /binwalk

# Install Binwalk dependencies
RUN sudo /binwalk/dependencies/ubuntu.sh

# Compile Binwalk
WORKDIR /binwalk
RUN cargo build --release

# Install compiled binwalk binary globally
RUN cp /binwalk/target/release/binwalk /usr/local/bin/binwalk

# Return to the app directory
WORKDIR /app

# Copy your application requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Default command
CMD ["python", "main.py"]