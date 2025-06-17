docker-compose build   

docker run -p 8888:8888 -it inf-jupyter 

# URL del stream de la cámara en la red (ajusta IP y puerto según la configuración)
url = "http://192.168.0.17:8080/video"

docker run --device=/dev/video0 -p 8888:8888 -it inf-jupyter