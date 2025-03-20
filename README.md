# Python web server for handling pi camera on rpi zero 2w
Not using another software because of performance.

## install 
sudo apt install python3-picamera2 --no-install-recommends
sudo apt-get install python3-opencv


### user
sudo useradd camerauser
sudo chown camerauser cert.pem
sudo chown camerauser key.pem
sudo chown camerauser main.py

#### so the user can access /dev/video
sudo usermod -a -G video camerauser 


### add service
sudo nano /etc/systemd/system/camera-server.service

then start it, and enable it

### create cert
sudo openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=192.168.1.*"

# Images
## Case outside
![case outside](./readme-media/case.png)

## Case inside
![case inside](./readme-media/in-case.png)