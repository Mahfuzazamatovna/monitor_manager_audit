import psutil
import datetime
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import time

def send_email_notification(sender_email, password, receiver_email, subject, message, attachment_path=None):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "plain"))

    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part["Content-Disposition"] = f"attachment; filename={os.path.basename(attachment_path)}"
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.mail.ru", 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
    except Exception as e:
        print(f"Не удалось отправить электронное письмо: {e}")

class EmailWindow:
    def __init__(self):
        self.sender_email = input("Email отправителя: ")
        self.sender_password = input("Пароль отправителя: ")
        self.recipient_email = input("Email получателя: ")

    def send_email(self):
        if self.sender_email and self.sender_password and self.recipient_email:
            try:
                send_email_notification(self.sender_email, self.sender_password, self.recipient_email, "Монитор процессов - Процессы", "Вложенный файл с процессами.", "processes.txt")
                print("Электронное письмо успешно отправлено!")
            except Exception as e:
                print(f"Произошла ошибка: {e}")
        else:
            print("Пожалуйста, заполните все поля.")

class ProcessMonitor:
    def __init__(self):
        self.monitoring = False
        self.paused = False
        self.update_interval = 1  # Интервал обновления в секундах
        self.processes = {}  # Словарь для хранения информации о процессах

    def start_monitoring(self):
        self.monitoring = True
        self.paused = False
        self.processes.clear()  # Очищаем словарь перед началом мониторинга
        self.monitor_processes()

    def pause_monitoring(self):
        self.paused = True

    def resume_monitoring(self):
        self.paused = False

    def stop_monitoring(self):
        self.monitoring = False
        self.paused = False
        self.save_processes()  # Сохраняем процессы при остановке мониторинга

    def monitor_processes(self):
        while self.monitoring:
            if not self.paused:
                for proc in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent', 'username']):
                    pid = str(proc.info['pid'])
                    if pid not in self.processes:
                        self.processes[pid] = proc.info
                        print(f"PID: {pid}, Name: {proc.info['name']}, CPU %: {proc.info['cpu_percent']:.2f}, Memory %: {proc.info['memory_percent']:.2f}, User: {proc.info['username']}, Date Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    else:
                        # Обновляем информацию о существующем процессе
                        print(f"Updated info for PID: {pid}, CPU %: {proc.info['cpu_percent']:.2f}, Memory %: {proc.info['memory_percent']:.2f}, Date Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.stop_monitoring()  # Остановка мониторинга после завершения сканирования всех процессов
            else:
                print("\nМониторинг приостановлен. Нажмите Enter, чтобы вернуться в меню...")
                input()
                break

    def save_processes(self):
        with open("processes.txt", "w") as f:
            for pid, info in self.processes.items():
                f.write(f"PID: {pid}\n")
                f.write(f"Name: {info['name']}\n")
                f.write(f"CPU %: {info['cpu_percent']:.2f}\n")
                f.write(f"Memory %: {info['memory_percent']:.2f}\n")
                f.write(f"User: {info['username']}\n")
                f.write(f"Date Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        print("Процессы успешно сохранены в файле processes.txt.")

def main():
    monitor = ProcessMonitor()
    email_window = EmailWindow()

    while True:
        choice = input("\nВыберите действие: \n1. Начать мониторинг\n2. Отправить процессы по почте\n3. Выйти\n")
        if choice == "1":
            monitor.start_monitoring()
        elif choice == "2":
            email_window.send_email()
        elif choice == "3":
            monitor.stop_monitoring()
            break
        else:
            print("Неверный выбор. Попробуйте еще раз.")

if __name__ == "__main__":
    main()
