#include <Wire.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_MPU6050.h>

// konfigurasi wifi
const char* ssid = "sokin ngab";
const char* password = "12345678";

// konfigurasi mqtt server
const int port = 1883;
const char* server = "34.101.48.71";
const char* mqtt_username = "";
const char* mqtt_password = "";

// konfigurasi mqtt topic
const char* accel_topic = "sensor/mpu6050/accel";
const char* gyro_topic = "sensor/mpu6050/gyro";

// set clientnya
Adafruit_MPU6050 mpu;
WiFiClient espClient;
PubSubClient client(espClient);

// membuat fungsi prototype
void reconnect();
void setup_wifi();
void callback(char* topic, byte* payload, unsigned int length);

void setup() {
  Wire.begin();
  Serial.begin(115200);
  
  if (!mpu.begin()) {
    Serial.println("Gagal menemukan perangkat MPU6050");
    while (1) {
      delay(10);
    }
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  setup_wifi();
  client.setServer(server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) { reconnect(); }
  client.loop();

  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);

  String gyro_data = String(gyro.gyro.x) + "," + String(gyro.gyro.y) + "," + String(gyro.gyro.z);
  String accel_data = String(accel.acceleration.x) + "," + String(accel.acceleration.y) + "," + String(accel.acceleration.z);

  client.publish(gyro_topic, gyro_data.c_str(), true);
  client.publish(accel_topic, accel_data.c_str(), true);
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Pesan diterima [");
  Serial.print(topic);
  Serial.print("] ");

  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Menyambungkan ke ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    Serial.print(" Status: ");
    Serial.println(WiFi.status());
  }

  Serial.println(" WiFi tersambung!");
  Serial.println("Alamat IP: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  
  while (!client.connected()) {
    Serial.println("Mencoba koneksi ke MQTT...");
    if (client.connect("ESP8266Client")) {
      Serial.println("Berhasil terkoneksi ke MQTT!");
      client.subscribe(accel_topic);
      client.subscribe(gyro_topic); 
    } else {
      Serial.print("Gagal, rc=");
      Serial.print(client.state());
      Serial.println(" Mencoba ulang dalam 5 detik...");
      delay(5000);
    }
  }
}
