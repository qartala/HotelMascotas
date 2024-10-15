from django.shortcuts import render, redirect, get_object_or_404
from transbank.error.transbank_error import TransbankError
from modulo.Producto.models import Reserva
from modulo.Compra.webpay_plus_settings import get_transaction
from django.urls import reverse
from transbank.webpay.webpay_plus.transaction import Transaction

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from transbank.error.transbank_error import TransbankError
from modulo.Producto.models import Reserva, Membresia
from modulo.Usuario.models import ReservaServicio, Usuario

def iniciar_pago(request, item_id, tipo_pago):
    # Obtener el item (reserva de habitación, servicio o membresía) según el tipo de pago
    if tipo_pago == 'habitacion':
        reserva = get_object_or_404(Reserva, id=item_id)
        amount = reserva.precio_total  # Monto a pagar para habitaciones
    elif tipo_pago == 'servicio':
        reserva = get_object_or_404(ReservaServicio, id=item_id)
        amount = reserva.precio  # Monto a pagar para servicios
    elif tipo_pago == 'membresia':
        membresia = get_object_or_404(Membresia, id=item_id)
        amount = membresia.valor  # Monto a pagar para membresías
    else:
        return render(request, 'base/usuario/error.html', {'error': 'Tipo de pago no válido'})

    # Configurar el monto y otros parámetros para el pago
    session_id = str(request.user.id)  # ID del usuario como session_id
    buy_order = str(item_id)  # ID del item como buy_order
    return_url = request.build_absolute_uri(reverse('pago_exitoso', kwargs={'tipo_pago': tipo_pago}))  # URL de retorno luego del pago exitoso

    try:
        # Crear transacción con Transbank
        transaction = get_transaction()
        response = transaction.create(buy_order, session_id, amount, return_url)
        print(response)
        return redirect(response['url'] + '?token_ws=' + response['token'])
    except TransbankError as e:
        return render(request, 'base/usuario/error.html', {'error': str(e)})


def pago_exitoso(request, tipo_pago):
    token = request.GET.get('token_ws')

    try:
        # Confirmar el pago
        transaction = get_transaction()
        response = transaction.commit(token)
        print(response)

        if response['status'] == 'AUTHORIZED':
            # Actualizar el estado según el tipo de pago
            item_id = response['buy_order']

            if tipo_pago == 'habitacion':
                reserva = get_object_or_404(Reserva, id=item_id)
                reserva.pagado = True  # Marcar la reserva de la habitación como pagada
                reserva.save()
            elif tipo_pago == 'servicio':
                reserva = get_object_or_404(ReservaServicio, id=item_id)
                reserva.pagado = True  # Marcar la reserva del servicio como pagada
                reserva.save()
            elif tipo_pago == 'membresia':
                membresia = get_object_or_404(Membresia, id=item_id)
                usuario = Usuario.objects.get(idUsuario=request.user)
                usuario.membresia = membresia  # Asociar la membresía al usuario
                usuario.save()
            else:
                return render(request, 'base/usuario/error.html', {'error': 'Tipo de pago no válido'})

            return render(request, 'base/usuario/pago_exitoso.html', {'item': item_id, 'response': response})
        else:
            return render(request, 'base/usuario/pago_fallido.html')
    except TransbankError as e:
        return render(request, 'base/usuario/error.html', {'error': str(e)})