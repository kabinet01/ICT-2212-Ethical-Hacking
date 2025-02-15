# Use an official Ubuntu image as a parent image
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages: SSH and FTP servers
RUN apt-get update && apt-get install -y \
    openssh-server \
    vsftpd \
    curl \
    make \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install sudo  

RUN mkdir /opt/sudo
WORKDIR /opt/sudo
RUN curl -O https://www.sudo.ws/dist/sudo-1.8.27.tar.gz
RUN tar xvfz sudo*.tar.gz
RUN mv sudo-1.8.27/* /opt/sudo/.
RUN ./configure
RUN make && make install

RUN echo 'FLAG: FLAG{w0w_c0ngr4ts_0n_g3ttIng_h3r3_pLz_sT0p_n0w}' > /root/flag.txt


# Configure SSH
RUN mkdir /var/run/sshd

# Add a new user 'jackie' and create .ssh directory for the user
RUN useradd -m -s /bin/bash jackie \
    && mkdir -p /home/jackie/.ssh \
    && chmod 700 /home/jackie/.ssh

# Copy the public key into jackie's authorized_keys (replace with your key)
COPY ./service/.ssh/id_rsa.pub /home/jackie/.ssh/authorized_keys
RUN chmod 600 /home/jackie/.ssh/authorized_keys 

COPY ./service/.ssh/id_rsa /home/jackie/.ssh/id_rsa
RUN chmod 644 /home/jackie/.ssh/id_rsa 
RUN chown -R jackie:jackie /home/jackie/.ssh \
    && chmod -R 755 /home/jackie/.ssh


RUN echo "jackie:juiceitup" | chpasswd

RUN usermod -aG sudo jackie
RUN echo "jackie ALL=(ALL,!root) /bin/bash" >> /etc/sudoers


RUN echo 'root:977yARY7aw3Y' | chpasswd
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
    && echo "AllowUsers jackie" >> /etc/ssh/sshd_config \
    && echo "AuthenticationMethods publickey" >> /etc/ssh/sshd_config \
    &&  echo "DenyUsers ftpuser" >>  /etc/ssh/sshd_config


# Configure vsftpd for FTP access without chroot
RUN echo "listen=NO" >> /etc/vsftpd.conf
RUN echo "listen_ipv6=YES" >> /etc/vsftpd.conf
RUN echo "anonymous_enable=NO" >> /etc/vsftpd.conf
RUN echo "local_enable=YES" >> /etc/vsftpd.conf
RUN echo "write_enable=YES" >> /etc/vsftpd.conf
RUN echo "chroot_local_user=NO" >> /etc/vsftpd.conf  # Disable chroot for users
RUN echo "allow_writeable_chroot=YES" >> /etc/vsftpd.conf
RUN echo "local_umask=022" >> /etc/vsftpd.conf  # Keep permissions readable for everyone
RUN echo "seccomp_sandbox=NO" >> /etc/vsftpd.conf  # Disable security sandbox


RUN useradd -m -s /bin/bash ftpuser && echo 'ftpuser:ftpuserpassword' | chpasswd
RUN mkdir -p /home/ftpuser/ftp && chmod 755 /home/ftpuser/ftp
RUN mkdir -p /var/run/vsftpd/empty
RUN chown -R ftpuser:ftpuser /home/ftpuser/ftp

# Expose SSH (port 22) and FTP (port 21)
EXPOSE 22 21

# Start both services (SSH and FTP) when the container starts
CMD service ssh start && vsftpd /etc/vsftpd.conf
