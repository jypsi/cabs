FROM fedora

RUN dnf -y update && dnf clean all
RUN dnf -y install python3-pip

ADD . /src

WORKDIR /src
RUN pip3 install -r requirements.txt
RUN python3 manage.py migrate

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
