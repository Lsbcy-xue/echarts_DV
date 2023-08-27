# myapp/management/commands/import_csv_DIBP.py
import csv
from django.core.management.base import BaseCommand
from charts.models import RegionData


class Command(BaseCommand):
    help = 'Imports data from a CSV file into the Item model'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')  # Assuming tab-separated values
            header = next(csv_reader)  # Read the header row

            for row in csv_reader:
                year = int(row[0])
                for idx, value in enumerate(row[1:], start=1):
                    region = header[idx]
                    metric_value = int(value)
                    RegionData.objects.create(
                        region=region,
                        year=year,
                        metric_value=metric_value
                    )

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))

