import csv, datetime, io
from ASP.models import User, ClinicManager, MedicineSupply, Order, Dispatcher, Location, Distance
from django.shortcuts import render, redirect, render_to_response
from django.views.generic.list import ListView
from django.http import HttpResponse, FileResponse, HttpResponseRedirect
from reportlab.pdfgen import canvas
from django.template import RequestContext

from .forms import SignupForm_1,LoginForm

def register(request):
    if request.method == 'POST':
        form = SignupForm_1(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            type = form.cleaned_data['type']
            email = form.cleaned_data['email']
            nu = User.objects.create(user_name = username, password=password, first_name=first_name, last_name=last_name, type=type, email=email)
            id_nextu = nu.id
            clinic_name = form.cleaned_data['clinic_name']
            clinic_location_name = form.cleaned_data['clinic_location_name']
            clinic_location_latitude = form.cleaned_data['clinic_location_latitude']
            clinic_location_longitude = form.cleaned_data['clinic_location_longitude']
            clinic_location_altitude = form.cleaned_data['clinic_location_altitude']
            dispatcher_name = form.cleaned_data['dispatcher_name']
            user_added = User.objects.get(id=id_nextu)
            if type =='CM':
                nl = Location.objects.create(name=clinic_location_name, latitude=clinic_location_latitude, longitude=clinic_location_longitude, altitude=clinic_location_altitude)
                id_nextl = nl.id
                location_added = Location.objects.get(id=id_nextl)
                ClinicManager.objects.create(user=user_added, name=clinic_name, location=location_added)
            elif type == 'DP':
                Dispatcher.objects.create(user=user_added, name=dispatcher_name)

            # More things to be done for the Warehouse personnel

            return HttpResponse('Register successed!')
    else:
        form = SignupForm_1()
    return render(request, 'register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.filter(user_name=username, password=password)
            if user:
                for us in user:
                    if us.type == 'CM':
                        response = HttpResponseRedirect('/asp/clinicmanager/add_order')
                    elif us.type == 'DP':
                        response = HttpResponseRedirect('/asp/dispatcher')
                    # More things to be done for warehouse personnel
                response.set_cookie('username', username, 3600)
                return response
            else:
                return HttpResponseRedirect('/login/')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout(request):
    response = HttpResponse('logout')
    response.delete_cookie('username')
    return response


# Create your views here.
class CMViewsSupply(ListView):
    template_name = 'ASP/clinicmanager.html'
    model = MedicineSupply
    clinic_manager = ClinicManager.objects.get(id=1) # change after login designed, haven't done yet
    max_weight = 23.8 # 25 - 1.2

    def construct_order(request):
        items = ''
        weight = 0.0
        for i in range(1, 10):
            amount = request.POST.get('amount' + str(i))
            if amount is None:
                break
            if amount != '':
                priority = request.POST.get('priority')
                amount = int(amount)
                id = request.POST.get('id' + str(i))
                name = request.POST.get('name' + str(i))
                weight += float(request.POST.get('weight' + str(i))) * amount
                items += "id: %s; name: %s; amount: %s.\n" %(id, name, amount)
        if items != '' and weight < CMViewsSupply.max_weight:
            CMViewsSupply.add_order(CMViewsSupply, items, weight, priority)

        return redirect('clinic-manager')

    def add_order(self, items, weight, priority):
        order = Order()

        order.clinic_manager = self.clinic_manager
        order.location = self.clinic_manager.location
        order.items = items
        order.weight = weight
        order.priority = priority
        order.timeQP = datetime.datetime.now()

        order.save()

        return


class WHViewsQueue(ListView):
    template_name = 'ASP/warehouse.html'
    ready_queue = []

    def get_queryset(self):
        return Order.objects.filter(status__contains='P').order_by('-priority')

    def update(request):
        order_id = request.POST.get('order')
        order = Order.objects.get(id=order_id)

        if order.status == 'QP':
            order.status = 'PW'
        elif order.status == 'PW':
            if order_id not in WHViewsQueue.ready_queue:
                return redirect('warehouse')
            order.status = 'QD'

        order.save()
        return redirect('warehouse')

    def get_rfid(request):
        order_id = request.POST.get('order')
        order = Order.objects.get(id=order_id)

        if order.status == 'PW':
            WHViewsQueue.ready_queue.append(order_id)

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="RFID.pdf"'
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer)
            p.drawString(100, 300, "Shipping Label.")
            p.drawString(100, 200, f'{order.clinic_manager}')
            p.drawString(100, 100, f'{order.location}')
            p.showPage()
            p.save()
            pdf = buffer.getvalue()
            buffer.close()
            response.write(pdf)
            return response

        return redirect('warehouse')


class DPViewsOrder(ListView):
    template_name = 'ASP/dispatcher.html'
    dispatcher = Dispatcher.objects.get(id=1) # change after login designed
    order_list = []
    total_weight = 0.0
    container_weight = 1.2
    max_weight = 25

    def get_queryset(self):
        return Order.objects.filter(status__exact='QD').order_by('-priority')

    def update_order(request):
        order_id = request.POST.get('order')
        order = Order.objects.get(id=order_id)
        weight = float(order.weight)

        if DPViewsOrder.total_weight + DPViewsOrder.container_weight + weight > DPViewsOrder.max_weight:
            return redirect('dispatcher')

        DPViewsOrder.total_weight += weight + DPViewsOrder.container_weight
        order.status = 'DI'
        order.dispatcher = DPViewsOrder.dispatcher
        order.timeDI = datetime.datetime.now()
        order.save()
        DPViewsOrder.order_list.append(order)
        return redirect('dispatcher')

    def get_csv(request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=dispacher_order.csv'
        writer = csv.writer(response)

        writer.writerow([f'Dispatcher {DPViewsOrder.dispatcher.id}', DPViewsOrder.dispatcher])

        hospital = Location.objects.get(name="Queen Mary Hospital")
        pre_location = hospital
        for order in DPViewsOrder.order_list:
            location = order.location
            location_obj = Location.objects.get(name=location)
            latitude = location_obj.latitude
            longtitude = location_obj.longitude
            altitude = location_obj.altitude
            if location == pre_location:
                writer.writerow([order.id, location, latitude, longtitude, altitude])
            #distance = Distance.objects.get(start=pre_location, end=location) # recover after distance stored
            writer.writerow([order.id, location, latitude, longtitude, altitude])#, distance]) # recover after distance stored
            pre_location = location

        location = hospital
        if location == pre_location:
            return redirect('dispatcher')

        # the last location is hosiptal
        #distance = Distance.objects.get(start=pre_location, end=location) # recover after distance stored
        writer.writerow([0, location, latitude, longtitude, altitude])#, distance]) # recover after distance stored

        DPViewsOrder.order_list.clear()
        DPViewsOrder.total_weight = 0
        return response
