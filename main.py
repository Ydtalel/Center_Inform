from random import choice, choices, randint, uniform
import string
import xml.etree.ElementTree as ET
from faker import Faker
import subprocess


class ChequeGenerator:
    """Класс для генерации и обработки XML-файлов чека"""

    def __init__(self, inn_file, ean_file):
        """Инициализирует объект генератора чека"""
        self.fake = Faker()
        self.alphabet = ('АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЭЮЯабвгдеёжзийклмнопрст'
                         'уфхцчшщьыэюя')
        self.INN_LIST = self.read_file(inn_file)
        self.EAN_LIST = self.read_file(ean_file)

    @staticmethod
    def read_file(file):
        """Читает файл и возвращает список строк"""
        with open(file, 'r') as f:
            return [line.strip() for line in f]

    @staticmethod
    def generate_barcode():
        """Генерирует случайный штрих-код, соответствующий заданному формату"""
        part1 = ''.join(choices(string.digits, k=2))
        part2 = 'N'
        part3 = ''.join(choices(string.ascii_letters + string.digits, k=20))
        part4 = choice(['0', '1'])
        part5 = choice(['0', '1', '2', '3'])
        part6 = ''.join(choices(string.digits, k=10))
        part7 = ''.join(choices(string.ascii_letters + string.digits, k=31))
        return f'{part1}{part2}{part3}{part4}{part5}{part6}{part7}'

    def generate_address(self):
        """Генерирует случайный адрес на основе русского алфавита"""
        length = randint(20, 100)
        return ''.join(choices(self.alphabet + '  ', k=length)).strip()

    def generate_name(self):
        """Генерирует случайное имя на основе русского алфавита"""
        length = randint(10, 20)
        return ''.join(choices(self.alphabet, k=length))

    @staticmethod
    def generate_kassa():
        """Генерирует случайный номер кассы"""
        length = randint(6, 12)
        return ''.join(choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def generate_volume():
        """Генерирует случайный volume"""
        volumes_list = [i / 100 for i in range(10, 305, 5)]
        return f'{choice(volumes_list):.4f}'

    @staticmethod
    def generate_datetime():
        """Генерирует случайную дату и время в формате ДДММГГЧЧММ"""
        day = randint(1, 31)
        month = randint(1, 12)
        year = randint(0, 99)
        hour = randint(0, 23)
        minute = randint(0, 59)
        return f'{day:02}{month:02}{year:02}{hour:02}{minute:02}'

    def generate_bottle(self):
        """Генерирует случайные данные для bottle"""
        return {
            'price': f'{uniform(100, 1000):.2f}',
            'barcode': self.generate_barcode(),
            'ean': choice(self.EAN_LIST),
            'volume': self.generate_volume()
        }

    def create_xml(self, file_name):
        """Создает файл чека"""
        cheque = ET.Element('Cheque', {
            'inn': choice(self.INN_LIST),
            'kpp': ''.join(choices(string.digits, k=9)),
            'address': self.generate_address(),
            'name': self.generate_name(),
            'kassa': self.generate_kassa(),
            'shift': str(randint(1, 10)),
            'number': str(randint(1, 100)),
            'datetime': self.generate_datetime()
        })

        count_bottles = randint(1, 10)
        for _ in range(count_bottles):
            bottle_data = self.generate_bottle()
            ET.SubElement(cheque, 'Bottle', bottle_data)

        tree = ET.ElementTree(cheque)
        tree.write(file_name, encoding='utf-8', xml_declaration=True)

    @staticmethod
    def send_xml(filename):
        """Отправляет XML-файл на сервер с помощью curl"""
        command = [
            'curl',
            '-F',
            f"xml_file=@{filename}",
            'http://localhost:8080/xml'
        ]
        subprocess.run(command)


if __name__ == "__main__":
    generator = ChequeGenerator('INN.txt', 'EAN.txt')
    generator.create_xml('cheque.xml')
    generator.send_xml('cheque.xml')
