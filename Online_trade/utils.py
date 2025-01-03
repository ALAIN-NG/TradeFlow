from Article.models import * 
from Orders.models import *
from Users.models import *
import json


def panier_cookie(request):
    try: 
        panier = json.loads(request.COOKIES.get('panier'))
    except:
        panier = {}    

    articles = []

    order = {
        'get_panier_total':0,
        'get_panier_article':0,
        'product_physic':False,
    }

    qty_article = order['get_panier_article']
    try:

        for obj in panier:
            qty_article += panier[obj]['qty']

            product = Article.objects.get(id=obj)

            total = (product.unit_price * panier[obj]['qty'])

            order['get_panier_article'] += panier[obj]['qty']

            order['get_panier_total'] += total

            article = {
                'product':{
                    'id': product.pk,
                    'name': product.name,
                    'unit_price': product.unit_price,
                    'image_url': product.image_url
                },

                'quantity': panier[obj]['qty'],
                'get_total': total
            }

            articles.append(article)
            order['product_physic'] = True
                
    except:
        pass 

    context = {
        'articles': articles,
        'order': order,
        'qty_article': qty_article
    }           

    return context


def data_cookie(request):

    if request.user.is_authenticated:

        client = request.user

        order = Invoice.objects.filter(save_by=client, customer=client)

        if not order:
            created = Invoice.objects.create(save_by=client, customer=client, total=0)

        order = Invoice.objects.filter(save_by=client, customer=client)

        articles = order[0].order_line_set.all()

   
        qty_article = order[0].get_panier_article

    else:
        
        cookie_panier = panier_cookie(request)
        articles = cookie_panier['articles']
        order = cookie_panier['order']
        qty_article = cookie_panier['qty_article']

    context = {
        'articles': articles,
        'order': order,
        'qty_article': qty_article
    }

    return context


# def commandeAnonyme(request, data):
#     print("utilisateur non authentifie")

#     print('cookies', request.COOKIES)
    
#     name = data['form']['name']
#     print('data', data)
#     print('name', name)
#     username = data['form']['username']
#     email = data['form']['email']
#     phone = data['form']['phone']

#     cookie_panier = panier_cookie(request)
#     articles = cookie_panier['articles']

#     client, created = Client.objects.get_or_create(
#         email = email
#     )
    
#     client.name = name
#     client.save()


#     order = Commande.objects.create(
#         client=client
#     )

#     for article in articles:
#         product = Product.objects.get(id=article['product']['id'])

#         order_line.objects.create(
#             product=product,
#             order = order,
#             quantity = article['quantity']
#         )

#     return client, order