import csv
from django.core.management.base import BaseCommand
from charts.models import IncomeData  # Replace 'your_app' with the actual name of your Django app


class Command(BaseCommand):
    help = 'Import income data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                IncomeData.objects.create(
                    year_quarter=row['年份_季度'],
                    total_income=int(row['居民人均可支配收入_累计值']),
                    wage_income=int(row['居民人均可支配工资性收入_累计值']),
                    business_income=int(row['居民人均可支配经营净收入_累计值']),
                    property_income=int(row['居民人均可支配财产净收入_累计值']),
                    transfer_income=int(row['居民人均可支配转移净收入_累计值']),
                )

        self.stdout.write(self.style.SUCCESS('Data imported successfully!'))
