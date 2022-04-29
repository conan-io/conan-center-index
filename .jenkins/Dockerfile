FROM ubuntu:21.04
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && apt-get install -y \
  git \
  gcc-8 \
  sudo \
  python3 \
  python3-pip \
  && rm -rf /var/lib/apt/lists/* \
  && pip3 install conan

RUN apt-get update && apt-get install -y \
  libx11-xcb-dev \
  pkg-config \
  libgtk2.0-dev \
  libfontenc-dev \
  libxaw7-dev \
  libxkbfile-dev \
  xorg-dev \
  libx11-xcb-dev \
  libxcb-render0-dev \
  libxcb-render-util0-dev \
  libxcb-icccm4-dev \
  libxcb-image0-dev \
  libxcb-keysyms1-dev \
  libxcb-randr0-dev \
  libxcb-shape0-dev \
  libxcb-xfixes0-dev \
  libxcb-xinerama0-dev \
  xkb-data \
  x11-xserver-utils \
  xorg \
  libxcb-util-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /docker_workdir
