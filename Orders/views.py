from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import HttpResponse
from .models import *
from django.db import transaction
import pdfkit
from django.template.loader import get_template
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import pagination, get_invoice
from django.utils.translation import gettext as _
from django.http import Http404, HttpResponseServerError


class HomeView(LoginRequiredMixin, View):
    """ Main view """

    # templates_name = 'index.html'

    invoices = Invoice.objects.select_related('customer', 'save_by').all().order_by('-invoice_date_time')

    page = 'home/'
    context = {
        'invoices': invoices,
        'page' : page
    }

    def get(self, request, *args, **kwargs):

        if request.user.role == 'S':
            templates_name = 'seller/index.html'

        else:
            templates_name = 'index.html'

        items = pagination(request, self.invoices)

        self.context['invoices'] = items

        return render(request, templates_name, self.context)
    
    
    def post(self, request, *args, **kwargs):

        # modify an invoice

        if request.user.role == 'S':
            templates_name = 'seller/index.html'

        else:
            templates_name = 'index.html'

        if request.POST.get('id_modified'):
            paid = request.POST.get('modified')

            try:

                obj = Invoice.objects.get(id = request.POST.get('id_modified'))

                if paid == 'True':
                    obj.paid = True

                else:
                    obj.paid = False

                obj.save()
                messages.success(request, _("Change made successfully."))

            except Exception as e:

                messages.error(request, f"Sorry, the following error has occurred {e}.")
        

        # deleting an invoive

        if request.POST.get('id_supprimer'):

            try:

                obj = Invoice.objects.get(pk = request.POST.get('id_supprimer'))
                obj.delete()

                messages.success(request, _("The deletion was successful."))
            
            except Exception as e:

                messages.error(request, f"Sorry, the following error has occurred {e}.")

        items = pagination(request, self.invoices)

        self.context['invoices'] = items

        return render(request, templates_name, self.context)
    

class AddInvoiceView(LoginRequiredMixin, View):
    template_name = 'add-invoice.html'

    def get(self, request, *args, **kwargs):
        customers = Person.objects.filter(role='C')
        articles = Article.objects.all()
        page = 'add-invoice/'
        context = {'customers': customers, 'articles': articles, 'page' : page}
        return render(request, self.template_name, context)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        try:

            # it = []
            # dattas = Article(
            # name = 'pc',
            # description = 'ordinateur',
            # quantity = 80,
            # unit_price = 200000,
            # save_by = request.user
            # )

            # it.append(dattas)
            # Article.objects.bulk_create(it)
            
            items = []
            customer = request.POST.get('customer')
            type = request.POST.get('invoice_type')
            articles = request.POST.getlist('article')
            qties = request.POST.getlist('qty')
            units = request.POST.getlist('unit')
            total_a = request.POST.getlist('total-a')
            total = request.POST.get('total')
            comment = request.POST.get('comment')

            # Check quantities first
            for index, article_name in enumerate(articles):
                article = Article.objects.filter(name=article_name).first()

                if article:
                    if int(article.quantity) < int(qties[index]):
                        messages.error(request, f"Insufficient quantity for {article_name}. Available: {article.quantity}.")
                        return render(request, self.template_name)
                else:
                    messages.error(request, f"Article {article_name} not found.")
                    return render(request, self.template_name)

            # If all quantities are valid, create the invoice and order lines
            invoice_object = {
                'customer_id': customer,
                'save_by': request.user,
                'total': total,
                'invoice_type': type,
                'comments': comment
            }

            invoices = Invoice.objects.create(**invoice_object)

            for index, article_name in enumerate(articles):
                article = Article.objects.get(name=article_name)
                article.quantity -= int(qties[index])
                article.save()

                data = Order_line(
                    invoice=invoices,
                    article_name=article,
                    quantity=qties[index],
                    unit_price=units[index],
                    total=total_a[index],
                )
                items.append(data)

            # Bulk create order lines
            created = Order_line.objects.bulk_create(items)

            if created:
                messages.success(request, _("Data saved successfully."))
                return redirect('home')
            else:
                messages.error(request, "Sorry, please try again. The sent data is corrupt.")

        except Exception as e:
            messages.error(request, f"An error occurred during invoice creation: {e}")
            return render(request, self.template_name)


class InvoiceVisualizationView(LoginRequiredMixin, View):
    """ This view helps to visualize the invoice """

    templates_name = 'invoice.html'

    def get(self, request, *args, **kwargs):

        pk = kwargs.get('pk')

        context = get_invoice(pk)

        context['page'] = f'view-invoice/{pk}/'

        return render(request, self.templates_name, context)


@login_required
def get_invoice_pdf(request, *args, **kwargs):
    """Generate PDF file from HTML file"""
    try:
        pk = kwargs.get('pk')
        context = get_invoice(pk)
        context['date'] = datetime.datetime.today()

        # Récupérer le template HTML
        template = get_template('invoice-pdf.html')

        # Rendre le template avec le contexte
        html = template.render(context)

        # Options pour le format PDF
        options = {
            'page-size': 'Letter',
            'encoding': 'UTF-8',
            'enable-local-file-access': ''
        }

        # Générer le PDF
        pdf = pdfkit.from_string(html, False, options)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = "attachment; filename='invoice_{}.pdf'".format(pk)

        return response

    except Exception as e:
        # Retourner une erreur 500 avec un message détaillé en cas d'exception
        return HttpResponseServerError(f"Erreur lors de la génération du PDF: {str(e)}")


class UpdateInvoiceView(LoginRequiredMixin, View):
    """ View to update an existing invoice """

    template_name = 'update-invoice.html'

    def get(self, request, pk, *args, **kwargs):
        try:
            invoice = Invoice.objects.get(id=pk)
            order_lines = Order_line.objects.filter(invoice=invoice)
            customers = Person.objects.filter(role='C')
            articles = Article.objects.all()
            page = f'invoice/update/{pk}/'
            context = {
                'invoice': invoice,
                'order_lines': order_lines,
                'customers': customers,
                'articles': articles,
                'page': page
            }
            return render(request, self.template_name, context)
        
        except Invoice.DoesNotExist:
            messages.error(request, "Invoice not found.")
            return redirect('home')

    def post(self, request, pk, *args, **kwargs):
        try:
            invoice = Invoice.objects.get(id=pk)

            # Mise à jour des champs de l'objet facture
            invoice.customer_id = request.POST.get('customer')
            invoice.invoice_type = request.POST.get('invoice_type')
            invoice.comments = request.POST.get('comment')
            invoice.total = request.POST.get('total')
            invoice.save()

            # Mise à jour des lignes de commande existantes
            Order_line.objects.filter(invoice=invoice).delete()  # Supprimer les lignes précédentes pour les remplacer
            articles = request.POST.getlist('article')
            qties = request.POST.getlist('qty')
            units = request.POST.getlist('unit')
            total_a = request.POST.getlist('total-a')

            # Check quantities first
            for index, article_name in enumerate(articles):
                article = Article.objects.filter(name=article_name).first()

                if article:
                    if int(article.quantity) < int(qties[index]):
                        messages.error(request, f"Insufficient quantity for {article_name}. Available: {article.quantity}.")
                        return render(request, self.template_name)
                else:
                    messages.error(request, f"Article {article_name} not found.")
                    return render(request, self.template_name)


            items = []
            for index, article in enumerate(articles):
                art = Article.objects.filter(name=article)
                item = Order_line(
                    invoice=invoice,
                    article_name=art[0],
                    quantity=qties[index],
                    unit_price=units[index],
                    total=total_a[index]
                )
                items.append(item)

            Order_line.objects.bulk_create(items)
            messages.success(request, _("Invoice updated successfully."))
            return redirect('home')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('update-invoice', pk=pk)
