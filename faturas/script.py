import pdfplumber
import re
import locale
import json
import glob
import datetime

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Expressões Regulares
reference_row = r'Valor\sa\spagar\s\(R\$\)\s*([\w ]+\s+)\s(\w+\/\d{4})\s+(\d{2}\/\d{2}\/\d{4})\s+(\d+,\d+)'
client_number_regex = r'Nº DA INSTALAÇÃO \d+\.\d+\.\d{4}\sàs\s\d{2}:\d{2}:\d{2}\s*(\d*)\s*(\d*)'
eletric_energy = r"Energia Elétrica kWh\s+(\d+)\s+(\d+,\d+)\s+(\d+,\d+)\s+(\d+,\d+)"
energy_scee_icms = r'Energia\sSCEE\ss\/\sICMS\skWh\s+(\d+\.?\d*)\s+(\d+,\d+)\s+(\d+,\d+)\s+(\d+,\d+)'
energy_gdi = r'Energia compensada\sGD\sI\skWh\s*(\d+\.?\d*)\s*(\d+,?\d*)\s*(\-?\d+,?\d+)\s*(\d+,?\d+)'
city_contribution = r'Contrib\sIlum\sPublica\sMunicipal\s*(\d+,?\d+)'

class EnergyMetric:
    def __init__(self, kwh: int, price: float) -> None:
        self.kwh = kwh
        self.price = price

    def to_json(self):
        return {"kwh": self.kwh, "price": self.price}

class Invoice:
    def __init__(self, client_number: str, reference_day: str, due_date: str, price: float, 
                 energy_eletric: EnergyMetric, energy_scee_icms: EnergyMetric, 
                 energy_gdi: EnergyMetric, city_contribution: float) -> None:
        
        self.client_number = client_number
        self.reference_date = reference_day
        self.due_date = due_date
        self.price = price
        self.energy_eletric = energy_eletric
        self.energy_scee_icms = energy_scee_icms
        self.energy_gdi = energy_gdi
        self.city_contribution = city_contribution

    def to_json(self):
        return {
            "client_number": self.client_number,
            "reference_date": self.reference_date,
            "due_date": self.due_date,
            "price": self.price,
            "energy_eletric": self.energy_eletric.to_json() if self.energy_eletric else None,
            "energy_scee_icms": self.energy_scee_icms.to_json() if self.energy_scee_icms else None,
            "energy_gdi": self.energy_gdi.to_json() if self.energy_gdi else None,
            "city_contribution": self.city_contribution,
            "scrape_date": datetime.datetime.now().isoformat()
        }

def parse_number(value: str):
    return locale.atof(value) if value else 0.0

def parse_eletric_metric(match):
    return EnergyMetric(parse_number(match[0]), parse_number(match[1])) if match else None

def safe_match(regex, text):
    match = re.search(regex, text, re.MULTILINE)
    return match.groups() if match else None

def build_invoice(text: str) -> Invoice:
    reference = safe_match(reference_row, text) or (None, None, None, "0,00")
    client_number = safe_match(client_number_regex, text) or ("0", "0")
    electric_energy = safe_match(eletric_energy, text) or ("0", "0,00")
    energy_scee_icms = safe_match(energy_scee_icms, text) or ("0", "0,00")
    energy_gdi = safe_match(energy_gdi, text) or ("0", "0,00")
    city_tax = parse_number(safe_match(city_contribution, text)[0]) if safe_match(city_contribution, text) else 0.0

    return Invoice(
        client_number[0], reference[1], reference[2], parse_number(reference[3]),
        parse_eletric_metric(electric_energy),
        parse_eletric_metric(energy_scee_icms),
        parse_eletric_metric(energy_gdi),
        city_tax
    )

def retrieve_invoice_data(filename):
    with pdfplumber.open(filename) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                return build_invoice(text)
    return None

if __name__ == "__main__":
    files = glob.glob("*.pdf")
    invoices = []

    for file in files:
        invoice = retrieve_invoice_data(file)
        if invoice:
            data = invoice.to_json()
            data["filename"] = file
            invoices.append(data)

    print(json.dumps(invoices, sort_keys=True, indent=4))
