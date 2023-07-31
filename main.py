import sqlite3
import sys
import requests , datetime
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5 import QtWidgets,QtCore
from PyQt5.Qt import Qt
from Icon_names import Icon_names
import SqlConnection
from datetime import datetime
from LanguageConvert import LanguageConvert
from Colors import Colors
class WeatherThread(QThread):
    weather_data_signal = pyqtSignal(dict)

    def __init__(self, city_name, api_key):
        super().__init__()
        self.city_name = city_name
        self.api_key = api_key

    def run(self):
        try:
            base_url = "http://api.openweathermap.org/data/2.5/weather"
            params = {"q": self.city_name, "appid": self.api_key, "units": "metric"}
            response = requests.get(base_url, params=params)
            data = response.json()
            self.weather_data_signal.emit(data)


        except Exception as e:
            error_data = {"cod": 404, "message": str(e)}
            self.weather_data_signal.emit(error_data)

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    def init_ui(self):
        self.setWindowTitle("Hava Durumu Uygulaması")
        self.weather_info_label = QLabel("Şehir Adı Girin:")
        self.city_input = QLineEdit()
        self.get_weather_button = QPushButton("Hava Durumu Al")
        self.infoLabel = QLabel()
        self.timelabel = QLabel(self)

        self.weather_images = Icon_names.weather_images
        self.weather_image_label = QLabel()
        self.weather_image_label.setPixmap(QPixmap())

        hb = QtWidgets.QHBoxLayout()
        hb.addWidget(self.weather_info_label)
        hb.addWidget(self.city_input)
        hb.addWidget(self.get_weather_button)

        hb2=QtWidgets.QHBoxLayout()
        hb2.addWidget(self.infoLabel)
        hb2.addWidget(self.weather_image_label)
        hb2.addStretch()

        vb = QtWidgets.QVBoxLayout()
        vb.addLayout(hb)
        vb.addLayout(hb2)
        vb.addStretch()
        vb.addWidget(self.timelabel)

        self.get_weather_button.clicked.connect(self.update_weather)
        self.setLayout(vb)

        background_color =Colors.background_color

        self.weather_info_label.setStyleSheet(background_color)
        self.setStyleSheet(background_color)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.update_weather()

    def update_weather(self):
        city_name = self.city_input.text()
        api_key = "1a595283a4468c1004251bd014da86d2"

        self.weather_thread = WeatherThread(city_name, api_key)
        self.weather_thread.weather_data_signal.connect(self.display_weather_data)
        self.weather_thread.start()
        self.timelabel.setText(QtCore.QDateTime.currentDateTime().toString())

    def display_weather_data(self, weather_data):

        hour = datetime.now().hour
        minute = datetime.now().minute
        Time = f"{hour}: {minute}"

        if weather_data["cod"] == 200:
            main_weather = weather_data["weather"][0]["description"]
            temperature = int(weather_data["main"]["temp"])
            humidity = weather_data["main"]["humidity"]
            wind_speed = weather_data["wind"]["speed"]

            weather_tr = LanguageConvert.weather_tr
            weather_en = LanguageConvert.weather_en

            for i in range(len(weather_en)):
                if main_weather == weather_en[i]:
                    main_weather = weather_tr[i]
                    image_path = self.weather_images.get(main_weather)
                    if image_path:
                        pixmap = QPixmap(image_path)
                        self.weather_image_label.setPixmap(pixmap)
                    break


            city_name = self.city_input.text().upper()
            info_label = self.infoLabel

            weather_text = f"\tHava Durumu: {main_weather}\n\n\tSıcaklık: {temperature} °C\n\n\tNem: {humidity}%\n\n\tRüzgar Hızı: {wind_speed} m/s"
            info_label.setText(f"\t     {city_name} \n\n{weather_text}")
            info_label.setFont(QFont('Helvetica',20))

            try:
                database = sqlite3.connect('database.db')
                c = database.cursor()
                c.execute("INSERT INTO weather VALUES (?, ?, ?, ?, ?, ?)",
                          (city_name, main_weather, temperature, humidity, wind_speed, Time))
                database.commit()
                database.close()
            except Exception as e:
                print("Veritabanına kayıt sırasında hata oluştu:", e)

        else:
            error_message = weather_data.get("error", "Hava durumu verileri alınamadı.")
            self.infoLabel.setText(error_message)
            self.weather_image_label.clear()


if __name__ == "__main__":
    SqlConnection.Sql_connect()
    app = QApplication(sys.argv)
    icon_path="Icons/logo.png"
    app.setWindowIcon(QIcon(icon_path))
    window = WeatherApp()
    window.setGeometry(400,200,500,400)
    window.show()
    sys.exit(app.exec_())
