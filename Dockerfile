FROM python:3.9

ADD main.py /
ARG BOT_TOKEN
ENV TOKEN=$BOT_TOKEN

RUN apt-get remove libexpat1 libexpat1-dev -y
RUN apt-get remove libsasl2-2 libsasl2-modules-db -y
RUN apt-get remove linux-libc-dev -y
RUN apt-get remove libssl-dev -y
RUN apt-get update -y
RUN apt-get install libexpat1>=2.2.10-2+deb11u1 -y
RUN apt-get install libsasl2-2>=2.1.27+dfsg-2.1+deb11u1 -y
RUN apt-get install libxslt1.1>=1.1.34-4+deb11u1
RUN apt-get install linux-libc-dev>=5.10.92-2 libc6-dev -y
RUN apt-get install zlib1g>=1:1.2.11.dfsg-2+deb11u1 -y
RUN apt-get install libxml2>=2.9.10+dfsg-6.7+deb11u3 -y
RUN apt-get install libksba8>=1.5.0-3+deb11u2 -y
RUN apt-get install git -y
RUN apt-get install libde265-0>=1.0.11-0+deb11u1 -y
#RUN apt-get install openssh-server>=1:9.2p1-2+deb12u2 -y

RUN pip install --upgrade pip
RUN pip install setuptools==65.5.1 requests==2.26.0 discord.py==2.3.2 aiohttp==3.9.0
