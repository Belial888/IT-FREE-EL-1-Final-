# core/models.py

from django.db import models
from django.contrib.auth.models import User

# Extends the built-in User model for specific resident/household data
class Beneficiary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200) # Beneficiary has a full_name field
    address = models.CharField(max_length=255) # Beneficiary has an address field
    contact_no = models.CharField(max_length=15, blank=True, null=True) # Beneficiary has a contact_no field
    household_info = models.TextField() # To store household information

    def __str__(self):
        return self.full_name

# Model for residents to submit aid requests
class AidRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('DISTRIBUTED', 'Distributed'), # Final status after distribution
    ]

    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE) # Linked to a beneficiary
    date_requested = models.DateTimeField(auto_now_add=True) # Has a date_requested field
    item_requested = models.CharField(max_length=100)
    quantity_requested = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Request for {self.item_requested} by {self.beneficiary.full_name}"

# Model to track distribution transactions
class Distribution(models.Model):
    request = models.ForeignKey(AidRequest, on_delete=models.SET_NULL, null=True) # Linked by a request_id
    barangay_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'is_staff': True}) # Staff who handled the distribution
    date_given = models.DateField() # Has a date_given field
    item_name = models.CharField(max_length=100) # Has an item_name field
    qty = models.IntegerField() # Has a qty (quantity) field
    recipient = models.CharField(max_length=200) # For tracking the recipient

    def __str__(self):
        return f"{self.item_name} distributed on {self.date_given}"