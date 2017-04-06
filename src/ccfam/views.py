from django.shortcuts import render


def home(request):
    # return HttpResponse("Hello, world. You're at the albums index.")
    return render(request, 'home.html', {})


def about(request):
    # return HttpResponse("Hello, world. You're at the albums index.")
    return render(request, 'about.html', {})


def contact(request):
    # return HttpResponse("Hello, world. You're at the albums index.")
    return render(request, 'contact.html', {})