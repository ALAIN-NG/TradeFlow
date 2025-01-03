from django.db.models import Sum
from datetime import datetime
from Orders.models import Order_line

def top_selling_articles(period='annually', label=None):
    """
    Retourne les articles les plus vendus pour une période donnée (annuelle uniquement).

    :param period: 'annually' uniquement
    :param label: année (ex. '2023') pour filtrer les données
    :return: Liste des articles les plus vendus avec leurs quantités ou une erreur si la période ou le label est invalide
    """
    filters = {}
    data = []

    try:
        if period == 'annually':  # Articles vendus par année
            year = int(label) if label else datetime.now().year  # Utilise l'année en cours si aucune n'est spécifiée
            filters['invoice__invoice_date_time__year'] = year

            data = (
                Order_line.objects.filter(**filters)
                .values('article_name__name')
                .annotate(total_quantity=Sum('quantity'))
                .order_by('-total_quantity')[:10]  # Limite à 10 articles les plus vendus
            )
        else:
            raise ValueError(f"Période invalide ou label manquant. Period: {period}, Label: {label}")

        # Formatter les données
        formatted_data = [
            {"article_name": item['article_name__name'], "total_quantity": item['total_quantity']}
            for item in data
        ]
        return formatted_data

    except ValueError as e:
        print(f"Erreur de valeur : {e}")
        return {"error": str(e)}

    except Exception as e:
        print(f"Erreur inattendue : {e}")
        return {"error": "Une erreur inattendue est survenue."}
