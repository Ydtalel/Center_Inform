import random
import string
import xml.etree.ElementTree as ET
from faker import Faker
import subprocess

fake = Faker()

alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЭЮЯабвгдеёжзийклмнопрстуфхцчшщьыэюя'


def read_file(file_name):
    with open(file_name, 'r') as file:
        return [line.strip() for line in file]


INN_LIST, EAN_LIST = read_file('INN.txt'), read_file('EAN.txt')


def generate_barcode():
    length = random.choice([20, 21, 30])
    return ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=length)
    )


def generate_address(chars):
    length = random.randint(20, 100)
    return ''.join(random.choices(chars + '  ', k=length)).strip()


def generate_name(chars):
    length = random.randint(10, 20)
    return ''.join(random.choices(chars, k=length))


def generate_kassa():
    length = random.randint(6, 12)
    return ''.join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )


def generate_volume():
    volumes_list = [i / 100 for i in range(10, 305, 5)]
    return f'{random.choice(volumes_list):.4f}'


def generate_bottle():
    return {
        'price': f'{random.uniform(100, 1000):.2f}',
        'barcode': generate_barcode(),
        'ean': random.choice(EAN_LIST),
        'volume': generate_volume()
    }


def create_xml(file_name):
    cheque = ET.Element('Cheque', {
        'inn': random.choice(INN_LIST),
        'kpp': ''.join(random.choices(string.digits, k=9)),
        'address': generate_address(alphabet),
        'name': generate_name(alphabet),
        'kassa': generate_kassa(),
        'shift': str(random.randint(1, 10)),
        'number': str(random.randint(1, 100)),
        'datetime': fake.date_time_this_year().strftime('%Y-%m-%dT%H:%M:%S')
    })

    num_bottles = random.randint(1, 10)
    for _ in range(num_bottles):
        bottle_data = generate_bottle()
        ET.SubElement(cheque, 'Bottle', bottle_data)

    tree = ET.ElementTree(cheque)
    tree.write(file_name, encoding='utf-8', xml_declaration=True)


def send_xml(filename):
    command = [
        'curl',
        '-F',
        f"xml_file=@{filename}",
        'http://localhost:8080/xml'
    ]
    subprocess.run(command)


if __name__ == "__main__":
    create_xml('cheque.xml')
    send_xml('cheque.xml')
