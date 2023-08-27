from django.db import models

# Create your models here.


# csv file: disposable_income_by_province.csv
class RegionData(models.Model):
    region = models.CharField(max_length=50)
    year = models.IntegerField()
    metric_value = models.IntegerField()

    def __str__(self):
        return f"{self.region} - {self.year}"


# csv file: income_and_inequality_metrics_national.csv
class Gini(models.Model):
    year_quarter = models.CharField(max_length=10)
    gini_coefficient = models.FloatField()
    disposable_income_growth = models.FloatField()
    median_disposable_income_growth = models.FloatField()
    wage_income_growth = models.FloatField()
    business_income_growth = models.FloatField()
    property_income_growth = models.FloatField()
    transfer_income_growth = models.FloatField()

    def __str__(self):
        return self.year_quarter

    class Meta:
        verbose_name_plural = "Gini Data"


# csv disposable_income_national.csv
class IncomeData(models.Model):
    year_quarter = models.CharField(max_length=10)  # e.g., "2014_Q一"
    total_income = models.IntegerField()
    wage_income = models.IntegerField()
    business_income = models.IntegerField()
    property_income = models.IntegerField()
    transfer_income = models.IntegerField()

    def __str__(self):
        return f"{self.year_quarter} - Total Income: {self.total_income}"

    class Meta:
        verbose_name_plural = "Income Data"
