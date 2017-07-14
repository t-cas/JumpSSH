FROM       ubuntu:16.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install --assume-yes apt-utils

RUN apt-get install -y openssh-server sudo
RUN mkdir /var/run/sshd

# allow root login
RUN echo 'root:password' |chpasswd
RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

## as default shell is /bin/sh
RUN ln -sf /bin/bash /bin/sh

## create individual user accounts
RUN useradd -ms /bin/bash user1 && \
echo "user1:password1" | chpasswd && \
chown -R user1:user1 /home/user1
RUN useradd -ms /bin/bash user2 && \
echo "user2:password2" | chpasswd && \
chown -R user2:user2 /home/user2
RUN useradd -ms /bin/bash user3 && \
echo "user3:password3" | chpasswd && \
chown -R user3:user3 /home/user3

# create sudoers file
RUN touch /etc/sudoers.d/my_sudoers

# give sudo permission to user1
RUN echo "user1	 ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/my_sudoers
# give sudo permission to user3
RUN echo "user3  ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/my_sudoers

RUN ssh-keygen -A

EXPOSE 22

CMD    ["/usr/sbin/sshd", "-D"]