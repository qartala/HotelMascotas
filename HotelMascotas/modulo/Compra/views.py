from django.shortcuts import render, redirect, get_object_or_404
from transbank.error.transbank_error import TransbankError
from modulo.Producto.models import Reserva
from modulo.Compra.webpay_plus_settings import get_transaction
from django.urls import reverse
from transbank.webpay.webpay_plus.transaction import Transaction

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from transbank.error.transbank_error import TransbankError
from modulo.Producto.models import Reserva, Membresia, ReservaRegalia
from modulo.Usuario.models import ReservaServicio, Usuario
from datetime import date
import sweetify


def iniciar_pago(request, item_id, tipo_pago):
    if tipo_pago == 'habitacion':
        reserva = get_object_or_404(Reserva, id=item_id)
        amount = reserva.precio_total  
    elif tipo_pago == 'servicio':
        reserva = get_object_or_404(ReservaServicio, id=item_id)
        amount = reserva.precio  
    elif tipo_pago == 'membresia':
        membresia = get_object_or_404(Membresia, id=item_id)
        amount = membresia.valor  
    else:
        return render(request, 'base/usuario/error.html', {'error': 'Tipo de pago no válido'})


    session_id = str(request.user.id)  
    buy_order = str(item_id)  
    return_url = request.build_absolute_uri(reverse('pago_exitoso', kwargs={'tipo_pago': tipo_pago}))  # URL de retorno luego del pago exitoso

    try:
        transaction = get_transaction()
        response = transaction.create(buy_order, session_id, amount, return_url)
        print(response)
        return redirect(response['url'] + '?token_ws=' + response['token'])
    except TransbankError as e:
        return render(request, 'base/usuario/error.html', {'error': str(e)})


def pago_exitoso(request, tipo_pago):
    token = request.GET.get('token_ws')

    try:
        transaction = get_transaction()
        response = transaction.commit(token)
        print(response)

        if response['status'] == 'AUTHORIZED':
            item_id = response['buy_order']  

            if tipo_pago == 'habitacion':
                reserva = get_object_or_404(Reserva, id=item_id)
                reserva.pagado = True
                reserva.save()

            elif tipo_pago == 'servicio':
                reserva = get_object_or_404(ReservaServicio, id=item_id)
                reserva.pagado = True
                reserva.save()

            elif tipo_pago == 'membresia':
                membresia = get_object_or_404(Membresia, id=item_id)
                usuario = Usuario.objects.get(idUsuario=request.user)


                usuario.membresia = membresia
                usuario.fecha_inicio_membresia = date.today()  
                usuario.save()

                sweetify.success(request, 'Membresía activada exitosamente.')

            else:
                return render(request, 'base/usuario/error.html', {'error': 'Tipo de pago no válido'})

            return render(request, 'base/usuario/pago_exitoso.html', {'item': item_id, 'response': response})

        else:
            return render(request, 'base/usuario/pago_fallido.html')

    except TransbankError as e:
        return render(request, 'base/usuario/error.html', {'error': str(e)})
    


## pagar regalos
def iniciar_pago_regalos(request, reserva_id):
    try:
        # Obtener la reserva de habitación especificada
        reserva = Reserva.objects.get(id=reserva_id, cliente=request.user, checkout=True)

        # Filtrar las ReservaRegalia asociadas a la reserva
        reservas_regalia = ReservaRegalia.objects.filter(reserva=reserva, pagada=False, usada=True)

        if not reservas_regalia.exists():
            return render(request, 'base/usuario/error.html', {'error': 'No tienes regalos pendientes de pago para esta reserva.'})

        # Calcular el monto total de las reservas de regalos asociadas
        amount = sum(regalia.precio_total_r for regalia in reservas_regalia)

        # Configurar la transacción
        session_id = str(request.user.id)
        buy_order = f"regalos-{reserva.id}-{request.user.id}"  # Orden de compra única por reserva
        return_url = request.build_absolute_uri(reverse('pago_exitoso_regalos', kwargs={'reserva_id': reserva.id}))  # URL de retorno luego del pago exitoso

        # Iniciar la transacción
        transaction = get_transaction()
        response = transaction.create(buy_order, session_id, amount, return_url)
        print(response)

        # Redirigir a la página de pago de Transbank
        return redirect(response['url'] + '?token_ws=' + response['token'])

    except Reserva.DoesNotExist:
        return render(request, 'base/usuario/error.html', {'error': 'Reserva de habitación no encontrada.'})

    except TransbankError as e:
        return render(request, 'base/usuario/error.html', {'error': str(e)})
    
def pago_exitoso_regalos(request, reserva_id):
    token = request.GET.get('token_ws')

    try:
        # Obtener la reserva de habitación especificada
        reserva = Reserva.objects.get(id=reserva_id, cliente=request.user, checkout=True)

        # Obtener las ReservaRegalia asociadas a esta reserva
        reservas_regalia = ReservaRegalia.objects.filter(reserva=reserva, pagada=False)

        if not reservas_regalia.exists():
            return render(request, 'base/usuario/error.html', {'error': 'No se encontraron regalos pendientes para esta reserva.'})

        # Confirmar el pago con Transbank
        transaction = get_transaction()
        response = transaction.commit(token)

        if response['status'] == 'AUTHORIZED':
            # Procesar las ReservaRegalia
            for regalia in reservas_regalia:
                if regalia.usada:
                    regalia.pagada = True  # Marcar como pagada si ha sido usada
                    regalia.save()
                else:
                    regalia.reserva = None  # Desasociar la reserva si no ha sido usada
                    regalia.save()

            # Mostrar la página de éxito
            return render(request, 'base/usuario/pago_exitoso_regalos.html', {
                'response': response,
                'reserva': reserva,
                'total_pagado': sum(regalia.precio_total_r for regalia in reservas_regalia if regalia.usada),
            })

        else:
            return render(request, 'base/usuario/pago_fallido.html', {'error': 'El pago no fue autorizado.'})

    except Reserva.DoesNotExist:
        return render(request, 'base/usuario/error.html', {'error': 'Reserva de habitación no encontrada.'})

    except TransbankError as e:
        return render(request, 'base/usuario/error.html', {'error': str(e)})