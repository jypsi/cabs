FROM fedora

RUN dnf -y update && dnf clean all
RUN dnf -y install python3-pip gcc python3-devel redhat-rpm-config postgresql-devel

WORKDIR /src

ADD requirements.txt /src/

RUN pip3 install -r requirements.txt

ADD data /src/data
ADD opencabs /src/opencabs
ADD finance /src/finance
ADD utils /src/utils
ADD manage.py /src/
ADD wsgi.py /src/

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
