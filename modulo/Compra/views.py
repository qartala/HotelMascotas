from django.shortcuts import render, redirect, get_object_or_404
from transbank.error.transbank_error import TransbankError
from modulo.Producto.models import Reserva
from modulo.Compra.webpay_plus_settings import get_transaction
from django.urls import reverse
from transbank.webpay.webpay_plus.transaction import Transaction

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from transbank.error.transbank_error import TransbankError
from modulo.Producto.models import Reserva
from modulo.Usuario.models import ReservaServicio

def iniciar_pago(request, reserva_id, tipo_reserva):
    # Obtener la reserva según el tipo de reserva
    if tipo_reserva == 'habitacion':
        reserva = get_object_or_404(Reserva, id=reserva_id)
        amount = reserva.precio_total  # Monto a pagar para habitaciones
    elif tipo_reserva == 'servicio':
        reserva = get_object_or_404(ReservaServicio, id=reserva_id)
        amount = reserva.precio  # Monto a pagar para servicios
    else:
        return render(request, 'base/usuario/error.html', {'error': 'Tipo de reserva no válido'})

    # Configurar el monto y otros parámetros para el pago
    session_id = str(request.user.id)  # ID del usuario como session_id
    buy_order = str(reserva.id)  # ID de la reserva como buy_order
    return_url = request.build_absolute_uri(reverse('pago_exitoso', kwargs={'tipo_reserva': tipo_reserva}))  # URL de retorno luego del pago exitoso

    try:
        # Crear transacción con Transbank
        transaction = get_transaction()
        response = transaction.create(buy_order, session_id, amount, return_url)
        print(response)
        return redirect(response['url'] + '?token_ws=' + response['token'])
    except TransbankError as e:
        return render(request, 'base/usuario/error.html', {'error': str(e)})

def pago_exitoso(request, tipo_reserva):
    token = request.GET.get('token_ws')

    try:
        # Confirmar el pago
        transaction = get_transaction()
        response = transaction.commit(token)
        print(response)

        if response['status'] == 'AUTHORIZED':
            # Actualizar el estado de la reserva
            reserva_id = response['buy_order']

            if tipo_reserva == 'habitacion':
                reserva = get_object_or_404(Reserva, id=reserva_id)
                reserva.pagado = True  # Marcar la reserva de la habitación como pagada
            elif tipo_reserva == 'servicio':
                reserva = get_object_or_404(ReservaServicio, id=reserva_id)
                reserva.pagado = True  # Marcar la reserva del servicio como pagada
            else:
                return render(request, 'base/usuario/error.html', {'error': 'Tipo de reserva no válido'})

            reserva.save()

            return render(request, 'base/usuario/pago_exitoso.html', {'reserva': reserva, 'response': response})
        else:
            return render(request, 'base/usuario/pago_fallido.html')
    except TransbankError as e:
        return render(request, 'base/usuario/error.html', {'error': str(e)})
