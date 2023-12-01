from django.db import models

PROCESS_CHOICES = (
    (1, 'Add Applicant'),
    (2, 'Update Applicant'),
    (3, 'Update Score'),
    (4, 'Add Major'),
    (5, 'Update Major'),
)
PAYMENT_CHOICES = (
        ("ERET", "english_retest"),
        ("REG", "registration_fees"),
        ("EQU", "Equation Fees")
    )


class OracleProcess(models.Model):
    applicant_id = models.IntegerField()
    email = models.EmailField()
    national_id = models.CharField(max_length=100)
    process = models.SmallIntegerField(choices=PROCESS_CHOICES)
    send = models.BooleanField(default=False)
    send_date = models.DateTimeField(blank=True, null=True)
    delivered = models.BooleanField(default=False)
    delivered_date = models.DateTimeField(blank=True, null=True)
    number_tries = models.SmallIntegerField(default=0)
    error_reason = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Oracle Process"
        verbose_name_plural = "Oracle Processes"


class PaymentOracleProcess(models.Model):
    applicant_id = models.IntegerField()
    email = models.EmailField()
    national_id = models.CharField(max_length=100)
    process = models.CharField(max_length=100, choices=PAYMENT_CHOICES)
    transaction_id = models.CharField(max_length=200)
    send = models.BooleanField(default=False)
    send_date = models.DateTimeField(blank=True, null=True)
    delivered = models.BooleanField(default=False)
    delivered_date = models.DateTimeField(blank=True, null=True)
    number_tries = models.SmallIntegerField(default=0)
    error_reason = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Payment Oracle Process"
        verbose_name_plural = "Payment Oracle Processes"
