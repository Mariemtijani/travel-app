from django.core.management.base import BaseCommand
from listings.models import User, Listing, Booking, Payment, Review, Message
from django.utils import timezone
from faker import Faker
from datetime import timedelta
import random
import uuid

fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with realistic sample data."

    def handle(self, *args, **kwargs):
        # Clear old data (optional)
        Message.objects.all().delete()
        Review.objects.all().delete()
        Payment.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write("🔄 Old data cleared.")

        # Create users
        users = []
        for _ in range(5):
            user = User.objects.create(
                user_id=uuid.uuid4(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                password_hash=fake.sha256(),
                phone_number=fake.phone_number(),
                role=random.choice(['guest', 'host']),
                created_at=timezone.now()
            )
            users.append(user)

        # Separate hosts and guests
        hosts = [u for u in users if u.role == 'host']
        guests = [u for u in users if u.role == 'guest']

        if not hosts or not guests:
            self.stdout.write(self.style.ERROR("⚠️ Need at least one host and one guest."))
            return

        # Create listings
        listings = []
        for _ in range(5):
            listing = Listing.objects.create(
                listing_id=uuid.uuid4(),
                host=random.choice(hosts),
                name=fake.sentence(nb_words=3),
                description=fake.paragraph(nb_sentences=2),
                location=fake.city(),
                price_per_night=round(random.uniform(40, 300), 2),
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            listings.append(listing)

        # Create bookings, payments, reviews
        for _ in range(10):
            guest = random.choice(guests)
            listing = random.choice(listings)
            start_date = fake.date_between(start_date="+1d", end_date="+10d")
            end_date = start_date + timedelta(days=random.randint(2, 5))
            days = (end_date - start_date).days
            total_price = round(listing.price_per_night * days, 2)

            booking = Booking.objects.create(
                booking_id=uuid.uuid4(),
                listing=listing,
                user=guest,
                start_date=start_date,
                end_date=end_date,
                total_price=total_price,
                status=random.choice(['pending', 'confirmed', 'canceled']),
                created_at=timezone.now()
            )

            Payment.objects.create(
                payment_id=uuid.uuid4(),
                booking=booking,
                amount=total_price,
                payment_date=timezone.now(),
                payment_method=random.choice(['credit_card', 'paypal', 'stripe'])
            )

            Review.objects.create(
                review_id=uuid.uuid4(),
                listing=listing,
                user=guest,
                rating=random.randint(1, 5),
                comment=fake.sentence(),
                created_at=timezone.now()
            )

        # Create messages
        for _ in range(10):
            sender, recipient = random.sample(users, 2)
            Message.objects.create(
                message_id=uuid.uuid4(),
                sender=sender,
                recipient=recipient,
                message_body=fake.sentence(),
                sent_at=timezone.now()
            )

        self.stdout.write(self.style.SUCCESS("✅ Database seeded with all models successfully!"))
