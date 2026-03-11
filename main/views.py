from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("<h1><a href='http://127.0.0.1:8000/author/'>Великий творец сайта</a>  <a href='http://127.0.0.1:8000/catalog/'>Страница магазина</a></h1>")

def catalog(request):
    return HttpResponse("<h1>Магазин спортивных товаров</h1>")

def author(request):
    return HttpResponse("<h1>Автор: Лоел Семён 89ТП</h1>")

def product_list():
    