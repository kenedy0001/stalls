# contacts/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Contact
from django.db.models import Q

def contact_list(request):
    query = request.GET.get('q', '')
    contacts = Contact.objects.filter(
        Q(full_name__icontains=query) |
        Q(email__icontains=query) |
        Q(phone__icontains=query)
    ).order_by('-id')

    if request.htmx:
        return render(request, 'contact_list_partial.html', {'contacts': contacts})
    return render(request, 'contact_list.html', {'contacts': contacts})


def contact_create(request):
    if request.method == 'POST':
        Contact.objects.create(
            full_name=request.POST['full_name'],
            email=request.POST['email'],
            phone=request.POST['phone']
        )
        contacts = Contact.objects.all().order_by('-id')
        return render(request, 'contact_list_partial.html', {'contacts': contacts})
    return HttpResponse(status=405)  # method not allowed


def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        contact.full_name = request.POST['full_name']
        contact.email = request.POST['email']
        contact.phone = request.POST['phone']
        contact.save()
        contacts = Contact.objects.all().order_by('-id')
        return render(request, 'contact_list_partial.html', {'contacts': contacts})
    return render(request, 'contact_update_form.html', {'contact': contact})


def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    contacts = Contact.objects.all().order_by('-id')
    return render(request, 'contact_list_partial.html', {'contacts': contacts})
