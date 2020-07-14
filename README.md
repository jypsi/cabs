# opencabs
An open source web framework to manage cab services

## Quickstart

### Using docker on Fedora

``` bash
sudo dnf install docker docker-compose -y
sudo systemctl enable docker; sudo systemctl start docker
sudo chcon -Rt svirt_sandbox_file_t $(pwd)

sudo docker-compose up -d

# Load sample data
sudo docker-compose run web python3 manage.py loaddata data/opencabs.json
```

### Using just Python on Fedora

``` bash
sudo dnf install -y python3-pip
sudo dnf -y install python3-pip gcc python3-devel redhat-rpm-config postgresql-devel
cd opencabs
python3 -m venv opencabs
source ./opencabs/bin/activate
pip install -r requirements.txt 
python3 manage.py migrate
python3 manage.py runserver
```

Update README

More changes
