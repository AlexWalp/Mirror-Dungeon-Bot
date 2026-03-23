FROM quay.io/pypa/manylinux_2_28_x86_64

RUN yum install -y zlib-devel bzip2-devel openssl-devel \
    libffi-devel readline-devel sqlite-devel xz-devel \
    libxcb xcb-util xcb-util-image xcb-util-keysyms xcb-util-renderutil \
    xcb-util-wm xcb-util-cursor libxkbcommon libxkbcommon-x11 \
    mesa-libGL gtk3 pango cairo gdk-pixbuf2 atk && \
    yum clean all

RUN curl https://pyenv.run | bash
ENV PATH="/root/.pyenv/bin:/root/.pyenv/shims:$PATH"

RUN PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.11.15
RUN pyenv global 3.11.15

WORKDIR /build
COPY requirements_linux.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements_linux.txt && \
    pip install pyinstaller

COPY . .

CMD ["bash", "release/linux/docker-linux.sh"]