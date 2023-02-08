FROM eclipse-mosquitto AS mosquitto-broker

# copy the configuration file
COPY config/mosquitto.conf /mosquitto/config/mosquitto.conf

# create username and password
RUN mosquitto_passwd -c -b /mosquitto/config/credentials admin admin  

# enable the password file in the configuration file
RUN sed -i 's/#password_file/password_file/' /mosquitto/config/mosquitto.conf