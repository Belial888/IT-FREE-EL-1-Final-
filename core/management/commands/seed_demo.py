from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Beneficiary, AidRequest, Distribution
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Seed demo data: users, beneficiaries, requests, and distributions'

    def handle(self, *args, **options):
        # Create staff user
        staff, created = User.objects.get_or_create(username='staff', defaults={'is_staff': True, 'email': 'staff@example.com'})
        if created:
            staff.set_password('password')
            staff.save()
            self.stdout.write('Created staff user (password: password)')

        # Create demo residents
        for i in range(1,6):
            username = f'resident{i}'
            user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
            if created:
                user.set_password('password')
                user.save()
            ben, _ = Beneficiary.objects.get_or_create(user=user, defaults={
                'full_name': f'Resident {i}',
                'address': f'123 Street {i}',
                'contact_no': f'0917123456{i}',
                'household_info': '2 adults, 2 children'
            })

            # Create a few requests
            for j in range(2):
                req = AidRequest.objects.create(
                    beneficiary=ben,
                    item_requested=random.choice(['Rice', 'Canned Goods', 'Water', 'Medicine']),
                    quantity_requested=random.randint(1,5),
                    status=random.choice(['PENDING','APPROVED','REJECTED'])
                )
                # Sometimes create a distribution
                if req.status == 'APPROVED' and random.random() > 0.5:
                    Distribution.objects.create(
                        request=req,
                        barangay_staff=staff,
                        date_given=timezone.now().date(),
                        item_name=req.item_requested,
                        qty=req.quantity_requested,
                        recipient=ben.full_name
                    )
        self.stdout.write(self.style.SUCCESS('Demo data seeded.'))
