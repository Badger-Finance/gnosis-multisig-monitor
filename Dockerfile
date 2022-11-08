FROM python:3.9

ADD main.py /
ARG BOT_TOKEN
ENV TOKEN=$BOT_TOKEN

RUN apt-get remove libexpat1 libexpat1-dev -y
RUN apt-get remove libsasl2-2 libsasl2-modules-db -y
RUN apt-get remove linux-libc-dev -y
RUN apt-get remove libssl-dev -y
RUN apt-get remove libtiff5 libtiffxx5 -y
RUN apt-get update -y
RUN apt-get install libssl-dev>=1.1.1k-1+deb11u2 libssl1.1>=1.1.1k-1+deb11u2 openssl>=1.1.1k-1+deb11u2 -y
RUN apt-get install libexpat1>=2.2.10-2+deb11u1 -y
RUN apt-get install libsasl2-2>=2.1.27+dfsg-2.1+deb11u1 -y
RUN apt-get install libxslt1.1>=1.1.34-4+deb11u1
RUN apt-get install linux-libc-dev>=5.10.92-2 libc6-dev -y
RUN apt-get install libtiff5>=4.2.0-1+deb11u1 -y
RUN apt-get install zlib1g>=1:1.2.11.dfsg-2+deb11u1 -y
RUN apt-get install libxml2>=2.9.10+dfsg-6.7+deb11u3 -y
RUN apt-get install git -y

RUN pip install requests==2.26.0 discord.py==1.7.3
