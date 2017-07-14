FROM jumpssh/image_sshd:latest

RUN apt-get install -y python-pip \
  && pip install --upgrade pip \
  && pip install flask -U \
  && rm -rf /var/cache/apk/* \
  && adduser -D app \
  && mkdir /restserver  \
  && chown -R app:app /restserver

USER app

# add directly the jar
ADD ../app.py /restserver/app.py

CMD python /restserver/app.py

EXPOSE 5000
