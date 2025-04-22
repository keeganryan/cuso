FROM sagemath/sagemath:latest

RUN sudo apt update && \
    sudo apt install -y \
    wget \
    cmake \
    python3 \
    libtool \
    fplll-tools \
    libfplll-dev \
    libgmp-dev \
    libmpfr-dev \
    libeigen3-dev \
    libblas-dev \
    liblapack-dev \
    libflint-dev \
    git

# 'sage' user should access the correct python interpreter
RUN sudo ln -sf $(sage -c "import sys; print(sys.executable)") /usr/bin/python3

USER sage

# Install dependencies

## msolve
RUN git clone https://github.com/algebraic-solving/msolve
WORKDIR /home/sage/msolve

RUN ./autogen.sh
RUN ./configure
RUN make dist && \
    make CFLAGS='-I/home/sage/sage/local/include' LDFLAGS='-L/home/sage/sage/local/lib' && \
    make check && \
    sudo make install

## flatter
WORKDIR /home/sage
RUN git clone https://github.com/keeganryan/flatter
WORKDIR /home/sage/flatter

RUN mkdir build
WORKDIR build
RUN cmake .. && make
RUN sudo make install
RUN sudo ldconfig

# Install cuso

## cuso
WORKDIR /home/sage
RUN git clone https://github.com/keeganryan/cuso.git
WORKDIR /home/sage/cuso

RUN sage --python3 -m pip install --upgrade pip
RUN sage --python3 -m pip install .

EXPOSE 4444

ENTRYPOINT ["sage", "-n", "jupyter", "--no-browser", "--ip=0.0.0.0", "--port=4444", "--log-level=ERROR"]
