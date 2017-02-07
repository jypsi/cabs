FROM fedora

RUN dnf -y update && dnf clean all
RUN dnf -y install python3-pip gcc python3-devel redhat-rpm-config postgresql-devel

ADD . /src

WORKDIR /src
RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
