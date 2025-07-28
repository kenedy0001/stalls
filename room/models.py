from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid
from django.conf import settings
from django.utils import timezone 




class MpesaExpressPayment(models.Model):
    CheckoutRequestID = models.CharField(max_length=50, blank=True, null=True)
    MerchantRequestID = models.CharField(max_length=20, blank=True, null=True)
    ResultCode = models.IntegerField(blank=True, null=True)
    ResultDesc = models.CharField(max_length=120, blank=True, null=True)
    Amount = models.FloatField(blank=True, null=True)
    MpesaReceiptNumber = models.CharField(max_length=15, blank=True, null=True)
    Balance = models.CharField(max_length=12, blank=True, null=True)
    TransactionDate = models.DateTimeField(blank=True, null=True)
    PhoneNumber = models.CharField(max_length=13, blank=True, null=True)

    def __str__(self):
        return f"{self.PhoneNumber} has sent {self.Amount} >> {self.MpesaReceiptNumber}"

class MpesaTillPayment(models.Model):
    TransactionType =  models.CharField(max_length=12, blank=True, null=True)
    TransID = models.CharField(max_length=12, blank=True, null=True)
    TransTime = models.CharField(max_length=14, blank=True, null=True)
    TransAmount = models.CharField(max_length=12, blank=True, null=True)
    BusinessShortCode = models.CharField(max_length=6, blank=True, null=True)
    BillRefNumber = models.CharField(max_length=20, blank=True, null=True)
    InvoiceNumber = models.CharField(max_length=20, blank=True, null=True)
    OrgAccountBalance = models.CharField(max_length=12, blank=True, null=True)
    ThirdPartyTransID = models.CharField(max_length=20, blank=True, null=True)
    MSISDN = models.CharField(max_length=12, blank=True, null=True)
    FirstName = models.CharField(max_length=20, blank=True, null=True)
    MiddleName = models.CharField(max_length=20, blank=True, null=True)
    LastName = models.CharField(max_length=20, blank=True, null=True)

    
class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, email, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Phone number is required')
        if not email:
            raise ValueError('Email is required')

        email = self.normalize_email(email)
        user = self.model(
            phone_number=phone_number,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.phone_number} ({self.email})"
class SpaceType(models.TextChoices):
    ROOM = 'room', 'Room'
    STALL = 'stall', 'Stall'

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey('Room', null=True, blank=True, on_delete=models.SET_NULL)
    stall = models.ForeignKey('Stall', null=True, blank=True, on_delete=models.SET_NULL)
    space_type = models.CharField(max_length=10, choices=SpaceType.choices)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def end_booking(self):
        self.end_time = timezone.now()
        self.is_active = False
        self.save()
        # Release the space
        if self.space_type == SpaceType.ROOM and self.room:
            self.room.release()
        elif self.space_type == SpaceType.STALL and self.stall:
            self.stall.release()

    def __str__(self):
        space = self.room.name if self.space_type == SpaceType.ROOM else self.stall.number
        return f"{self.user} booked {self.space_type.title()} {space}"

class SpaceStatus(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    OCCUPIED = 'occupied', 'Occupied'
    MAINTENANCE = 'maintenance', 'Under Maintenance'
    RESERVED = 'reserved', 'Reserved'


class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=300, null=True)
    size_in_sq_meters = models.FloatField()
    status = models.CharField(
        max_length=20,
        choices=SpaceStatus.choices,
        default=SpaceStatus.AVAILABLE
    )
    image = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_available(self):
        return self.status == SpaceStatus.AVAILABLE

    def book(self):
        if self.is_available():
            self.status = SpaceStatus.OCCUPIED
            self.save()
            return True
        return False

    def release(self):
        if self.status in [SpaceStatus.OCCUPIED, SpaceStatus.RESERVED]:
            self.status = SpaceStatus.AVAILABLE
            self.save()
            return True
        return False

    @classmethod
    def add_room(cls, name, size, image=None):
        return cls.objects.create(name=name, size_in_sq_meters=size, image=image)

    @classmethod
    def available_rooms(cls):
        return cls.objects.filter(status=SpaceStatus.AVAILABLE)

    def __str__(self):
        return f"Room {self.name} ({self.get_status_display()})"


class Stall(models.Model):
    number = models.CharField(max_length=20, unique=True)
    room = models.ForeignKey(Room, related_name='stalls', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=SpaceStatus.choices,
        default=SpaceStatus.AVAILABLE
    )
    image = models.CharField(  blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_available(self):
        return self.status == SpaceStatus.AVAILABLE

    def book(self):
        if self.is_available():
            self.status = SpaceStatus.OCCUPIED
            self.save()
            return True
        return False

    def release(self):
        if self.status in [SpaceStatus.OCCUPIED, SpaceStatus.RESERVED]:
            self.status = SpaceStatus.AVAILABLE
            self.save()
            return True
        return False

    @classmethod
    def add_stall(cls, number, room, image=None):
        return cls.objects.create(number=number, room=room, image=image)

    @classmethod
    def available_stalls(cls):
        return cls.objects.filter(status=SpaceStatus.AVAILABLE)

    def __str__(self):
        return f"Stall {self.number} in {self.room.name} ({self.get_status_display()})"