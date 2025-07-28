from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib import messages
from datetime import timedelta
import random
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Room, Stall, Booking, SpaceType,SpaceStatus
from django.db.models import Q
User = get_user_model()



def generate_code():
    return str(random.randint(100000, 999999))

# --- Public views (no login required) ---

def signup_view(request):
    if request.method == 'POST':
        from .forms import UserCreationForm 
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created. Please log in.")
            return redirect('login')
        else:
            messages.error(request, 'Invalid credentials , Check and reenter again')
    else:
        from .forms import UserCreationForm
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        password = request.POST.get('password')
        user = authenticate(request, phone_number=phone, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'logs.html')

def send_verification_code(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        try:
            user = User.objects.get(phone_number=phone)
            code = generate_code()
            user.verification_code = code
            user.save()

            # Send Email
            send_mail(
                subject="Your Verification Code",
                message=f"Your verification code is: {code}",
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.info(request, f"Verification code sent to {user.email}")
            return redirect('verify_account')
        except User.DoesNotExist:
            messages.error(request, "Phone number not found.")
    return render(request, 'send_code.html')

def verify_account(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        code = request.POST.get('code')
        try:
            user = User.objects.get(phone_number=phone)
            if user.verification_code == code:
                user.is_verified = True
                user.verification_code = None
                user.save()
                messages.success(request, "Account verified!")
                return redirect('login')
            else:
                messages.error(request, "Invalid code.")
        except User.DoesNotExist:
            messages.error(request, "Phone number not found.")
    return render(request, 'verify.html')

def reset_password(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        try:
            user = User.objects.get(phone_number=phone)
            if user.verification_code == code:
                user.set_password(new_password)
                user.verification_code = None
                user.save()
                messages.success(request, "Password reset. You may now log in.")
                return redirect('login')
            else:
                messages.error(request, "Invalid verification code.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")
    return render(request, 'reset_password.html')

# --- Protected views (require login) ---

def dashboard(request): 
    query = request.GET.get("q", "")
    rooms = Room.objects.filter(
        Q(name__icontains=query),  status=SpaceStatus.AVAILABLE
    )
    if request.htmx:
        return render(request, 'rooms.html', {'rooms': rooms})
    return render(request, 'dashboard.html',{'rooms':rooms})


 

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect('dashboard')




@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    user = User.objects.get(phone_number=request.user.phone_number)
    print(room, user) 
    if room.is_available():
        try:
            Booking.objects.create(
                user=user,
                room=room,
                space_type=SpaceType.ROOM,
                start_time=timezone.now(),
                end_time=timezone.now() + timedelta(days=2)
            )
            room.status = SpaceStatus.OCCUPIED
            room.save()
            return redirect('dashboard')
        except Exception as e:
            return render(request, 'error.html', {'message': str(e)})
    return render(request, 'pay.html')

@login_required
def pay(request):
    pass

 

 