from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
from django.contrib.auth.decorators import login_required
from .utils import data_cookie
from Article.models import * 
from Orders.models import *
from Users.models import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.html import strip_tags
from Orders.utils import *


# Create your views here.
def index(request):
    product = Article.objects.exclude(image_url='')
    data = data_cookie(request)
    nombre_article = data['qty_article']

    context = {
        'products':product,
        'nombre_article': nombre_article
    }
    return render(request, 'client.html', context)
    

def panier(request, *args, **kwargs):
    """ panier """
    
    data = data_cookie(request)
    articles = data['articles']
    order = data['order']
    qty_article = data['qty_article']

    context = {
        'articles':articles,
        'order':order[0],
        'nombre_article':qty_article
    }

    return render(request, 'panier.html', context)


def order(request, *args, **kwargs):
    """ order """

    data = data_cookie(request)
    articles = data['articles']
    order = data['order']
    qty_article = data['qty_article']

    context = {
        'articles':articles,
        'order':order[0],
        'nombre_article': qty_article
    }

    return render(request, 'order.html', context)    



@login_required
def update_article(request, *args, **kwargs):

    data = json.loads(request.body)

    product_pk = data['product_id']

    action = data['action']

    client = request.user

    product = Article.objects.get(pk=product_pk)

    order, created = Invoice.objects.get_or_create(
        save_by=client, customer=client, defaults={'total': 0}
    )

    order.invoice_type = 'R'
    order.save()

    order_article, created = Order_line.objects.get_or_create(
        invoice=order, article_name=product,
        defaults={
            'total': product.unit_price,
            'quantity': 0,
            'unit_price': product.unit_price
        }
    )

    if action == 'add':
        order_article.quantity += 1
    elif action == 'remove':
        order_article.quantity -= 1

    if order_article.quantity <= 0:
        order_article.delete()
    else:
        order_article.total = order_article.quantity * order_article.unit_price
        order_article.save()

    return JsonResponse({"message": "Article mis à jour"}, safe=False)


@login_required
def traitementOrder(request, *args, **kwargs):
    """ traitement,  validation de la com;ande  et verification de l'integrite des donnees(detection de fraude)"""

    STATUS_TRANSACTION = ['ACCEPTED', 'COMPLETED', 'SUCESS']

    data = json.loads(request.body)

    print(data)

    client = request.user

    order, created = Invoice.objects.get_or_create(
        save_by=client, customer=client, defaults={'total': 0}
    )


    total = float(data['form']['total'])

    order.total = total
    print(total, order.get_panier_total)
    if float(order.get_panier_total) == total:

        """Send an email to the customer amd a seller"""
        try:
            address = data['shipping']['address'],
            date = data['shipping']['date'],
            hour = data['shipping']['hour']
            client = request.user
            # Récupérer la commande depuis la base de données
            order = Invoice.objects.get(save_by=client, customer=client)

            pk = order.pk

            context = get_invoice(pk)

            context['date'] = datetime.datetime.today()

            template = get_template('invoice-online.html')

            custom_email = request.user.email 

            seller_email = 'alaingildasngueudjang@gmail.com'

            # render html with context variables
            html = template.render(context)
            
            # Charger le template HTML pour l'email
            sujet1 = "Votre facture d'achat"

            sujet2 = "Nouvelle commande, information de livraison: "

            text_content = strip_tags(html)  # Version texte sans HTML


            # Créer l'email
            email = EmailMultiAlternatives(
                subject=sujet1,
                body=text_content,  # Message texte ou HTML
                from_email='alain.ng.tech@gmail.com',  # Expéditeur
                to=[custom_email],  # Destinataire
            )
            email.attach_alternative(html, "text/html")  # Ajouter le contenu HTML
            
            # Envoyer l'email
            email.send()


            # Créer l'email
            email = EmailMultiAlternatives(
                subject=f" {sujet2}\t Address: {address}\t Date: {date}\t hour: {hour}",
                body=text_content,  # Message texte ou HTML
                from_email='alain.ng.tech@gmail.com',  # Expéditeur
                to=[seller_email],  # Destinataire
            )
            email.attach_alternative(html, "text/html")  # Ajouter le contenu HTML
            
            # Envoyer l'email
            email.send()
            order.delete() 
        except order.DoesNotExist:
            return JsonResponse("Erreur: La commande que vous essayez de valider n'exite pas!", safe=False)

        except Exception as e:
            return JsonResponse(f"Erreur lors de l'envoi de l'email : {e}", safe=False)

    else:
        
        return JsonResponse("Attention!!! Traitement Refuse Fraude detecte!", safe=False)


    return JsonResponse("Votre commande a été enregistrée avec succès, vous recevrez votre facture dans un instant !", safe=False)


