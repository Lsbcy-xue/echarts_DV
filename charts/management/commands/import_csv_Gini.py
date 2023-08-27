import csv
from charts.models import Gini
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import Gini data from CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip header row

            for row in csv_reader:
                Gini.objects.create(
                    year_quarter=row[0],
                    gini_coefficient=float(row[1]),
                    disposable_income_growth=float(row[2]),
                    median_disposable_income_growth=float(row[3]),
                    wage_income_growth=float(row[4]),
                    business_income_growth=float(row[5]),
                    property_income_growth=float(row[6]),
                    transfer_income_growth=float(row[7])
                )

        self.stdout.write(self.style.SUCCESS('Gini data imported successfully.'))
