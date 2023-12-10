import sys
import sqlite3
import time
from sensor import sensor
from PyQt6 import QtWidgets
from PyQt6 import uic
from PySide6.QtCore import QTimer



class sensor_ui():
    def __init__(self):
        #initialize the window
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = uic.loadUi("form.ui")
        self.window.show()
        self.temp_sensor = sensor()
        self.n = 0 #this will be used for tracking the 10x counter
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.read_single_button(n=True))        
        
        #database connection
        self.conn = sqlite3.connect("sensor_data.db")
        self.cursor = self.conn.cursor()
        
        #callback bindings
        self.window.read_single_button.clicked.connect(self.read_single_button)
        self.window.read_10x_button.clicked.connect(self.read_10x_button)
        self.window.calculate_statistics_button.clicked.connect(self.calculate_statistics_button)
        self.window.close_button.clicked.connect(self.close_button)
        
        
        #set default valuies
        self.window.temperature_alarm_input.setText("100.0")
        self.window.humidity_alarm_input.setText("50.0")        
        
        #run
        self.app.exec()
        
        
    def read_single_button(self, n=False):
        '''Callback for the read single button
            n = (bool) True if this call is from the 10x button, false if not
        '''
        #method gets called when you click the read single button
    
        #self.n gets used to track how many readings have been read in the 10x function
        if n:
            self.n += 1
        
        #read data
        now, temp, humidity = self.temp_sensor.read()
        
        #insert into sqlite3 database
        cmd = f"""INSERT INTO data ('timestamp', 'temperature', 'humidity') VALUES ('{now}', {temp}, {humidity})"""
        self.cursor.execute(cmd)
        self.conn.commit()
        
        #update UI
        self.window.current_temp_input.setText(str(round(temp, 2)))
        self.window.current_humidity_input.setText(str(round(humidity, 2)))
        
        #check for alarms
        try:
            temp_alarm = float(self.window.temperature_alarm_input.text())
            humidity_alarm = float(self.window.humidity_alarm_input.text())        
        except:
            self.window.status_input.setText("Error parsing alarm values")
            
        temp_too_high = (temp >= temp_alarm)
        humidity_too_high = (humidity >= humidity_alarm)
            
        #update the status window
        if not n:
            self.window.status_input.setText(f"Single Read\n\nTemp alarm={temp_too_high}\n\nHumidity alarm={humidity_too_high}")
        else:
            self.window.status_input.setText(f"Read {self.n}\n\nTemp alarm={temp_too_high}\n\nHumidity alarm={humidity_too_high}")
            
        if n and (self.n >= 10):
            self.timer.stop()
            self.n = 0            
        
    def read_10x_button(self):
        '''Callback for the read 10x button'''
        
        #A Qtimer is already bound to read_single_button
        #read_single_button will track how many times its been called and stop after 10x
        #all we have to do here is use the button to start the timer, at intervals of 1000ms= 1s
        self.timer.start(1000)
    
    def calculate_statistics_button(self):
        '''Read the last 10 lines from the sql database and display statistics'''
    
        cmd = "SELECT * from data ORDER BY id DESC LIMIT 10"
        result = self.cursor.execute(cmd).fetchall()
        
        temps = []
        humidities = []
        
        for row in result:
            temps.append(round(row[2], 2))
            humidities.append(round(row[3], 2))
            
        self.window.status_input.setText(f"Statistics\n\nTemp min/max/avg = {min(temps)}/{max(temps)}/{round(sum(temps)/len(temps),2)}\n\nHumidity min/max/avg = {min(humidities)}/{max(humidities)}/{round(sum(humidities)/len(humidities),2)}")
        
    def close_button(self):
        sys.exit()
        
        
        
def main():
    root = sensor_ui()

if __name__ == '__main__':
    main()
