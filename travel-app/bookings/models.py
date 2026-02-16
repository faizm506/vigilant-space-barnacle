import uuid
from django.db import models
from django.utils import timezone

class Booking(models.Model):
    booking_id = models.CharField(
        max_length=50, # Increased length to fit the brand name
        unique=True, 
        editable=False, 
        verbose_name="Booking UID"
    )

    PAYMENT_CHOICES = [
        ('Pending', 'Pending'),
        ('Partial', 'Partial'),
        ('Paid', 'Paid'),
    ]
    payment_status = models.CharField(
        max_length=10, 
        choices=PAYMENT_CHOICES, 
        default='Pending'
    )
    
    # 2. Basic Information
    customer_name = models.CharField(max_length=200)
    address = models.TextField()
    total_members = models.PositiveIntegerField(default=1)
    
    # 3. Passport Photo (Stored locally in /media/passports/)
    passport_photo = models.ImageField(upload_to='passports/', null=True, blank=True)
    tour_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # 4. The "10 Other Fields" (Dynamic Data)
    # This stores the manager's custom fields as a dictionary
    # Example: {"meal_pref": "Veg", "hotel_stars": "5", "visa_status": "Approved"}
    additional_info = models.JSONField(default=dict, blank=True)
    
    # 5. Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.booking_id:
            # Loop until we find a unique ID (just in case)
            while True:
                date_str = timezone.now().strftime('%Y%m')
                unique_code = uuid.uuid4().hex[:6].upper()
                new_id = f"RS-{date_str}-{unique_code}"
                
                # Check if this ID already exists in the database
                if not self.__class__.objects.filter(booking_id=new_id).exists():
                    self.booking_id = new_id
                    break
        
        # Ensure this line is aligned with the 'if' statement
        super().save(*args, **kwargs)