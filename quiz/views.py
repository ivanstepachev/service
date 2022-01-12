from django.shortcuts import render, redirect, get_object_or_404
from quiz.models import Order, Token
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import json

import requests

admin_id = 896205315


def quiz(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        type_of_cake = request.POST.get('type_of_cake')
        message = request.POST.get('message')
        order = Order(name=name, phone=phone, type_of_cake=type_of_cake, message=message)
        order.save()
        order_text = f'''Имя: {order.name}
        Телефон: {order.phone}
        Десерт: {order.type_of_cake}
        Примечание: {order.message}
        https://caketeam.herokuapp.com/orders/{order.id}'''
        send_message(chat_id=admin_id, text=order_text)
        return redirect('quiz')
    else:
        return render(request, 'quiz/index.html')


def orders(request):
    orders = Order.objects.all()
    return render(request, 'quiz/orders.html', {'orders': orders})


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        note = request.POST.get('note')
        order.note = note
        order.save()
        order_text = f'''Десерт: {order.type_of_cake}
                Примечание: {order.message}
                Примечание 2: {order.note}'''
        send_message(chat_id=admin_id, text=order_text)
        return redirect('quiz')
    return render(request, 'quiz/order_detail.html', {'order': order})


def send_message(chat_id, text):
    method = "sendMessage"
    token = Token.objects.get(id=1).token
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


@csrf_exempt
def bot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(data)
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        send_message(chat_id=chat_id, text=text)
    return HttpResponse('ok', content_type='text/plain', status=200)


def setwebhook(request):
    if request.method == "POST":
        token = request.POST.get('token')
        link = request.POST.get('link')
        token_exist = Token.objects.filter(id=1)
        if token_exist:
            new_token = token_exist[0]
            new_token.token = token
            new_token.save()
        else:
            new_token = Token(id=1, token=token)
            new_token.save()
        requests.get(f'https://api.telegram.org/bot{token}/setWebhook?url=https://{link}/bot')
        return redirect('setwebhook')
    else:
        url = request.build_absolute_uri().split('/')[2]
        return render(request, 'quiz/setwebhook.html', {'url': url})


def deletewebhook(request):
    if request.method == "POST":
        token = request.POST.get('token')
        requests.get(f'https://api.telegram.org/bot{token}/deleteWebhook')
        return redirect('deletewebhook')
    else:
        token = Token.objects.filter(id=1)
        return render(request, 'quiz/deletewebhook.html', {'token': token})


# {'update_id': 541049445, 'message':
#     {'message_id': 60, 'from':
#         {'id': 896205315, 'is_bot': False, 'first_name': 'Ivan', 'username': 'ivan40', 'language_code': 'ru'},
#      'chat': {'id': 896205315, 'first_name': 'Ivan', 'username': 'ivan40', 'type': 'private'},
#      'date': 1641148166, 'text': 'Hdbcnf'}}