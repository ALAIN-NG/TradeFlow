from django.shortcuts import render, redirect
from Article.models import Article
from Users.models import Person
from Orders.models import Invoice, Order_line
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from Users.utils import pagination
from django.db.models.functions import TruncMonth, TruncYear , TruncDay
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import timedelta
from django.utils import timezone
from datetime import datetime
from .utils import top_selling_articles 
from django.http import JsonResponse
from django.db.models.functions import ExtractYear
from decimal import Decimal
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _


@login_required
def admin_dashboard(request):
    """
    Affiche le tableau de bord de l'administrateur si l'utilisateur a le rôle 'administrateur'.
    Si l'utilisateur n'a pas ce rôle, il est redirigé vers la page de connexion.
    """
    if request.user.role != 'A':
        return redirect('login')  # Redirection si l'utilisateur n'est pas administrateur
    return render(request, 'admin_dashboard.html')




@login_required
def client_page(request):
    """
    Affiche la page du client, accessible uniquement aux utilisateurs connectés avec le rôle 'client'.
    """
    return render(request, 'client.html')


def vendeur_page(request):
    """
    Affiche la page du vendeur.
    """
    return render(request, 'vendeur.html')


def administrateur_page(request):
    """
    Affiche la page de l'administrateur.
    """
    return render(request, 'administrateur.html')




def view_sales_stats(request):
    """
    Affiche des statistiques sur les ventes :
    - Le nombre total de commandes
    - Le chiffre d'affaires total
    - Les ventes par vendeur
    """

    # Nombre total de lignes de commande
    total_sales = Order_line.objects.count()

    # Chiffre d'affaires total
    total_revenue = Order_line.objects.aggregate(total_revenue=Sum('unit_price'))['total_revenue'] or 0

    # Ventes par vendeur : total des commandes par vendeur
    sales_by_seller = Invoice.objects.values('id')\
                                       .annotate(total_sales=Count('id'))\
                                       .order_by('id')

    # Rendu de la page avec les statistiques
    return render(request, 'view_sales_stats.html', {
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'sales_by_seller': sales_by_seller
    })




class manager_dashboard(LoginRequiredMixin, View):
    
    templates_name = 'manager/article-view.html'

    articles = Article.objects.all().order_by('id')

    page = 'article-view/'

    context = {
        'articles': articles,
        'page' : page
    }

    def get(self, request, *args, **kwargs):

        items = pagination(request, self.articles)

        self.context['articles'] = items

        return render(request, self.templates_name, self.context)
    
    
    def post(self, request, *args, **kwargs):


        # deleting a Article

        if request.POST.get('id_supprimer'):

            try:

                obj = Article.objects.get(pk = request.POST.get('id_supprimer'))
                obj.delete()

                messages.success(request, _("The deletion was successful."))
            
            except Exception as e:

                messages.error(request, f"Sorry, the following error has occurred {e}.")

        items = pagination(request, self.articles)

        self.context['articles'] = items

        return render(request, self.templates_name, self.context)


def seller_dashboard(request):
    """
    Affiche le tableau de bord du vendeur.
    L'utilisateur doit avoir le rôle 'S' pour accéder à cette vue.
    """
    if request.user.role != 'S':
        return redirect('login')

    return render(request, 'seller-dashboard.html')


@login_required
def manage_clients(request):
    """
    Permet à l'administrateur de gérer les clients : afficher, ajouter, modifier ou supprimer des clients.
    """
    persons = Person.objects.filter(role='C')
    

    context = {
        'persons': persons,
    }

    items = pagination(request, persons)

    context['persons'] = items

    if request.user.role == 'S':
        template_name = 'seller/manage_clients.html'

    else:
        template_name = 'manage_clients.html'

    
    if request.POST.get('id_supprimer'):

        try:

            obj = Person.objects.get(pk = request.POST.get('id_supprimer'))
            obj.delete()

            messages.success(request, _("The deletion was successful."))
        
        except Exception as e:

            messages.error(request, f"Sorry, the following error has occurred {e}.")

    items = pagination(request, persons)

    context['persons'] = items

    return render(request, template_name, context)



@login_required
def manage_sellers(request):
    """
    Permet à l'administrateur de gérer les vendeurs : afficher, ajouter, modifier ou supprimer des vendeurs.
    """
    persons = Person.objects.filter(role='S')
    items = pagination(request, persons)

    context = {
        'persons': persons,
    }

    if request.POST.get('id_supprimer'):

        try:

            obj = Person.objects.get(pk = request.POST.get('id_supprimer'))
            obj.delete()

            messages.success(request, _("The deletion was successful."))
        
        except Exception as e:

            messages.error(request, f"Sorry, the following error has occurred {e}.")

    items = pagination(request, persons)

    context['persons'] = items
    return render(request, 'manage_sellers.html', context)

@login_required
def manage_managers(request):
    """
    Permet à l'administrateur de gérer les gestionnaires : afficher, ajouter, modifier ou supprimer des gestionnaires.
    """
    persons = Person.objects.filter(role='M')
    items = pagination(request, persons)

    context = {
        'persons': persons,
    }

    if request.POST.get('id_supprimer'):

        try:

            obj = Person.objects.get(pk = request.POST.get('id_supprimer'))
            obj.delete()

            messages.success(request, _("The deletion was successful."))
        
        except Exception as e:

            messages.error(request, f"Sorry, the following error has occurred {e}.")

    items = pagination(request, persons)

    context['persons'] = items

    return render(request, 'manage_managers.html', context)

@login_required
def manage_articles(request):
    """
    Permet de gérer les articles : afficher, ajouter, modifier ou supprimer des articles.
    """
    articles = Article.objects.all()
    items = pagination(request, articles)
    return render(request, 'manage_articles.html', {'articles': items})



def sales_by_period(period='annually', label=None):
    """Retourne les ventes par période (année, mois ou jour) sous forme de données."""
    filters = {}
    data = []

    if period == 'daily' and label:  # Ventes par jour
        year, month = map(int, label.split('-'))  # Ex : "2023-02"
        filters['invoice_date_time__year'] = year
        filters['invoice_date_time__month'] = month
        data = (
            Invoice.objects.filter(**filters)
            .annotate(label=TruncDay('invoice_date_time'))
            .values('label')
            .annotate(value=Sum('total'))
            .order_by('label')
        )
    elif period == 'monthly' and label:  # Ventes par mois
        year, month = map(int, label.split('-'))  # Ex : "2015-01" → year = 2015, month = 1
        filters['invoice_date_time__year'] = year
        filters['invoice_date_time__month'] = month
        data = (
            Invoice.objects.filter(**filters)
            .annotate(label=TruncMonth('invoice_date_time'))
            .values('label')
            .annotate(value=Sum('total'))
            .order_by('label')
        )
    elif period == 'annually':  # Ventes par année
        data = (
            Invoice.objects.annotate(label=TruncYear('invoice_date_time'))
            .values('label')
            .annotate(value=Sum('total'))
            .order_by('label')
        )

    # Transformation des dates pour un affichage lisible
    formatted_data = [
        {"label": item['label'].strftime('%Y-%m-%d' if period == 'daily' else '%Y-%m'),
         "value": item['value']}
        for item in data
    ]
    return formatted_data


# def top_articles(request):
#     period = request.GET.get('period', 'annually')  # période par défaut : annuelle
#     label = request.GET.get('label', None)  # label par défaut : None

#     # Si aucun label n'est fourni, utiliser l'année actuelle
#     if not label:
#         label = str(datetime.now().year)  # Utiliser l'année actuelle par défaut

#     # Récupérer les articles les plus vendus pour la période et le label (uniquement annuelle ici)
#     articles = top_selling_articles(period=period, label=label)

#     # Préparer les données pour l'affichage graphique
#     labels = [article['article_name'] for article in articles]
#     quantities = [article['total_quantity'] for article in articles]

#     # Découper le label pour extraire l'année
#     year = label  # L'année est directement extraite du label
#     month = None
#     day = None

#     # Si la requête est AJAX, renvoyer les données en JSON
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         return JsonResponse({
#             'labels': labels,
#             'quantities': quantities
#         })
#     else:
#         # Les années disponibles pour filtrer
#         years = Order_line.objects.values('invoice__invoice_date_time__year').distinct().order_by('invoice__invoice_date_time__year')

#         for i in range(len(years)):
#             year1 = years[i]
#         context = {
#             'labels': labels,
#             'quantities': quantities,
#             'period': period,
#             'label': label,
#             'year': year,
#             'years': year1,
#         }

#     return context



def seller_performance():
    """Retourne la performance des vendeurs."""
    data = (
        Invoice.objects.values('save_by__name')
        .annotate(total_sales=Sum('total'))
        .order_by('-total_sales')
    )
    return list(data)


def paid_unpaid_invoices():
    """Retourne le total des factures payées et impayées."""
    data = {
        'paid': Invoice.objects.filter(paid=True).aggregate(total=Sum('total'))['total'] or 0,
        'unpaid': Invoice.objects.filter(paid=False).aggregate(total=Sum('total'))['total'] or 0,
    }
    return data


def sales_trends():
    """Retourne les tendances des ventes."""
    data = (
        Invoice.objects.annotate(year=TruncYear('invoice_date_time'))
        .values('year')
        .annotate(total_sales=Sum('total'))
        .order_by('year')
    )
    formatted_data = [
        {"label": item['year'].strftime('%Y'), "value": item['total_sales']}
        for item in data
    ]
    return formatted_data


def promote_expiring_articles(threshold_days=30, limit=15):
    """
    Met en promotion les articles les moins vendus dont la date de péremption approche.
    """
    expiration_limit = timezone.now().date() + timedelta(days=threshold_days)

    # Récupérer les articles qui expirent bientôt et qui sont les moins vendus
    articles_to_promote = Article.objects.filter(
        date_per__lte=expiration_limit
    ).order_by('quantity')[:limit]  # Trier par quantité croissante

    # Créer une liste de dictionnaires sérialisables
    promoted_articles_list = []
    for article in articles_to_promote:
        promoted_articles_list.append({
            'name': article.name,
            'quantity': article.quantity
        })

    return promoted_articles_list  # Retourner la liste de dictionnaires


def dashboard(request):
    """Affiche le tableau de bord avec toutes les données nécessaires au rendu des graphiques."""
    annual_data = sales_by_period(period='annually')
    monthly_data = []
    daily_data = []

    paid_unpaid_data = paid_unpaid_invoices_by_year_api(request)

    first_year = datetime.now().year
    # Générer les données pour toutes les années, mois et jours disponibles
    for year_data in annual_data:
        year = year_data['label']
        monthly = sales_by_period(period='monthly', label=year)
        monthly_data.extend(monthly)

        for month_data in monthly:
            month_label = month_data['label']
            daily = sales_by_period(period='daily', label=month_label)
            daily_data.extend(daily)

    # Ajouter toutes les données au contexte
    context = {
        'annual_data': json.dumps(annual_data, cls=DjangoJSONEncoder),
        'monthly_data': json.dumps(monthly_data, cls=DjangoJSONEncoder),
        'daily_data': json.dumps(daily_data, cls=DjangoJSONEncoder),
        'top_articles': chart_view(request),
        'seller_performance': json.dumps(seller_performance(), cls=DjangoJSONEncoder),
        # 'paid_unpaid': json.dumps(paid_unpaid_invoices(), cls=DjangoJSONEncoder),
        'paid_unpaid': paid_unpaid_data,
        'first_year' : first_year,
        'sales_trends': json.dumps(sales_trends(), cls=DjangoJSONEncoder),
        'promote_expiring_articles' : json.dumps(promote_expiring_articles(), cls=DjangoJSONEncoder),
    }
    return render(request, 'dashboard.html', context)


def chart_view(request):
    period = request.GET.get('period', 'annually')  # période par défaut : annuelle
    label = request.GET.get('label', None)  # label par défaut : None

    # Si aucun label n'est fourni, utiliser l'année actuelle
    if not label:
        label = str(datetime.now().year)  # Utiliser l'année actuelle par défaut

    # Récupérer les articles les plus vendus pour la période et le label (uniquement annuelle ici)
    articles = top_selling_articles(period=period, label=label)

    # Préparer les données pour l'affichage graphique
    labels = [article['article_name'] for article in articles]
    quantities = [article['total_quantity'] for article in articles]

    # Découper le label pour extraire l'année
    year = label  # L'année est directement extraite du label
    month = None
    day = None

    # Si la requête est AJAX, renvoyer les données en JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'labels': labels,
            'quantities': quantities
        })
    else:
        # Les années disponibles pour filtrer
        years = Order_line.objects.values('invoice__invoice_date_time__year').distinct().order_by('invoice__invoice_date_time__year')
        years1 = []
        for i in range(len(years)):
            years1.append(years[i])
        
        context = {
            'labels': labels,
            'quantities': quantities,
            'period': period,
            'label': label,
            'year': year,
            'years': years1,
        }
    return context


def paid_unpaid_invoices_by_year_api(request):
    """
    API qui retourne les données des factures payées et impayées pour chaque année.
    """
    # Extraire toutes les années uniques des factures
    invoices = Invoice.objects.annotate(invoice_year=ExtractYear('invoice_date_time'))
    years = invoices.values_list('invoice_year', flat=True).distinct()

    # Préparer les données pour chaque année
    data = []
    for year in years:
        year_invoices = invoices.filter(invoice_year=year)
        data.append({
            'year': year,
            'paid': float(year_invoices.filter(paid=True).aggregate(total=Sum('total'))['total'] or 0),
            'unpaid': float(year_invoices.filter(paid=False).aggregate(total=Sum('total'))['total'] or 0),
        })

    # Retourner les données sous forme de réponse JSON
    return list(data)