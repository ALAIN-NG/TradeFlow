from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)
from .models import *

def pagination(request, invoices):

    # default_page
    default_page = 1

    page = request.GET.get('page', default_page)

    # paginate items

    items_per_page = 5

    parginator = Paginator(invoices, items_per_page)

    try:

        items_page = parginator.page(page)

    except PageNotAnInteger:

        items_page = parginator.page(default_page)
    
    except EmptyPage:

        items_page = parginator.page(parginator.num_pages)

    return items_page


def get_invoice(pk):
    """ Get invoice function """

    obj = Invoice.objects.get(pk=pk)

    articles = obj.order_line_set.all()

    context = {
        'obj': obj,
        'articles': articles,
    }

    return context