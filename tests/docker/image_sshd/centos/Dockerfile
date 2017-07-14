FROM centos:centos7

RUN yum -y update
RUN yum install -y initscripts openssh-server sudo
#RUN yum -y update && yum install -y initscripts openssh openssh-server openssh-clients sudo passwd sed screen tmux byobu which vim-enhanced
#RUN sshd-keygen
#RUN sed -i "s/#UsePrivilegeSeparation.*/UsePrivilegeSeparation no/g" /etc/ssh/sshd_config && sed -i "s/UsePAM.*/UsePAM no/g" /etc/ssh/sshd_config

# allow root login
RUN echo 'root:password' |chpasswd
RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

# cleanup to reduce image size
RUN rm -rf /tmp/*

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