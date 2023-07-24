# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
from typing import Tuple, Optional

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi
from playsound import playsound


class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("clock_app_interface.ui", self)
        self.screen_time = 0
        self.sound_path = None
        self.MusicB.clicked.connect(self.music_select)
        self.rb_check()
        self.ResetB.clicked.connect(self.reset)
        self.AnulujB.clicked.connect(self.stop_timer)
        self.ClockRB.toggled.connect(lambda: self.connect_function(False, self.clock_time))
        self.TimerRB.toggled.connect(lambda: self.connect_function(True, self.timer_time))
        self.StopwatchRB.toggled.connect(lambda: self.connect_function(False, self.stopwatch_time))
        self.AlarmRB.toggled.connect(lambda: self.connect_function(True, self.alarm_time))
        self.RemainingRB.toggled.connect(lambda: self.connect_function(True, self.time_remaining))

    def music_select(self):
        selected_files, _ = QFileDialog.getOpenFileName(self, "Wybierz plik", "", "Pliki MP3 (*.mp3)")
        if selected_files:
            self.sound_path = os.path.normpath(selected_files)

    def music_play(self) -> bool:
        if self.sound_path is None:
            self.EkranLabel.setText("Nie wybrano pliku z dźwiękiem ")
            return False
        else:
            return True

    def start_b_change(self):
        self.StartB.setEnabled(False)
        self.ResetB.setEnabled(False)
        self.AnulujB.setEnabled(True)

    def cancel_b_change(self):
        self.StartB.setEnabled(True)
        self.ResetB.setEnabled(True)
        self.AnulujB.setEnabled(False)

    def clean_screen(self):
        self.EkranLabel.setText(" ")

    def stop_timer(self):
        self.timer.stop()
        self.cancel_b_change()

    def reset_time(self):
        self.screen_time = 0

    def reset(self):
        self.clean_screen()
        self.reset_time()

    def clock_time(self):
        self.start_b_change()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.clock)
        self.timer.start(1000)

    def stopwatch_time(self):
        self.reset_time()
        self.start_b_change()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.stopwatch)
        self.timer.start(1000)

    def timer_time(self):
        self.reset_time()
        if self.music_play():
            minute, seconds = self.check_time()
            if minute is not None or seconds is not None:
                self.start_b_change()
                self.screen_time = (int(minute) * 60) + int(seconds)
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.timer_zegar)
                self.timer.start(1000)
        else:
            return

    def alarm_time(self):
        if self.music_play():
            hour, minute = self.check_time()
            if hour is not None or minute is not None:
                self.start_b_change()
                self.screen_time = (int(hour) * 60) + int(minute)
                self.EkranLabel.setText(f"Budzik jest ustawiony na {int(hour):02d}:{int(minute):02d}")
                self.timer = QTimer()
                self.timer.timeout.connect(self.alarm)
                self.timer.start(1000)
            else:
                return
        else:
            return

    def line_edit_status(self, status: bool):
        self.HourLE.setEnabled(status)
        self.MinuteLE.setEnabled(status)

    def connect_function(self, set_status: bool, function_name: callable):
        self.StartB.clicked.disconnect()
        self.line_edit_status(set_status)
        self.StartB.clicked.connect(function_name)

    def rb_check(self):
        if self.ClockRB.isChecked():
            self.StartB.clicked.connect(self.clock_time)
            self.line_edit_status(False)
        if self.TimerRB.isChecked():
            self.StartB.clicked.connect(self.timer_time)
            self.line_edit_status(False)
        if self.StopwatchRB.isChecked():
            self.StartB.clicked.connect(self.stopwatch_time)
            self.line_edit_status(False)
        if self.AlarmRB.isChecked():
            self.StartB.clicked.connect(self.alarm_time)
            self.line_edit_status(True)
        if self.RemainingRB.isChecked():
            self.StartB.clicked.connect(self.time_remaining)
            self.line_edit_status(True)

    def alarm(self):
        current_time = ((int(datetime.now().hour)) * 60) + int(
            datetime.now().minute)
        if self.screen_time == current_time:
            self.EkranLabel.setText(f"Nastała wybrana godzina ")
            self.stop_timer()
            playsound(self.sound_path)

    def clock(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        self.EkranLabel.setText(current_time)

    def time_remaining(self):
        hour, minute = self.check_time()
        if hour is None or minute is None:
            self.EkranLabel.setText("błedne dane")
        else:
            hour_now = datetime.now().hour
            minute_now = datetime.now().minute
            hour = int(self.HourLE.text())
            minute = int(self.MinuteLE.text())
            result = ((hour - hour_now) * 60) + (minute - minute_now)
            if result >= 0:
                self.EkranLabel.setText(f"Do podanej godziny zostało: {(result // 60):02d}:{(result % 60):02d}")
            else:
                self.EkranLabel.setText(f"Do podanej godziny zostało: {(24 + (result // 60)):02d}:{(result % 60):02d}")

    def check_time(self) -> Tuple[Optional[int], Optional[int]]:
        hour = self.HourLE.text()
        minute = self.MinuteLE.text()
        if hour.isdigit() and minute.isdigit():
            if 0 <= int(hour) < 24 and 0 <= int(minute) < 60:
                return hour, minute
        hour, minute = None, None
        self.EkranLabel.setText(f"Podano błędne wartości ")
        return hour, minute

    def stopwatch(self):
        self.screen_time += 1
        minutes = self.screen_time // 60
        seconds = self.screen_time % 60
        self.EkranLabel.setText(f"{minutes:02d}:{seconds:02d}")

    def timer_zegar(self):
        if self.screen_time == 0:
            playsound(self.sound_path)
            self.stop_timer()
        else:
            self.screen_time -= 1
            minutes = self.screen_time // 60
            seconds = self.screen_time % 60
            self.EkranLabel.setText(f"{minutes:02d}:{seconds:02d}")


app = QApplication(sys.argv)
mainwindow = MainWindow()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedHeight(600)
widget.setFixedWidth(600)
widget.show()

sys.exit(app.exec())
