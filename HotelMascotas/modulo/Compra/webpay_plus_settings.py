from transbank.webpay.webpay_plus.transaction import Transaction, WebpayOptions
from transbank.common.integration_type import IntegrationType

# Configura Transbank para ambiente de pruebas (sandbox)
commerce_code = '597055555532'  # Código de comercio de Webpay Plus
api_key = '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C'  # API Key Secret de prueba

def get_transaction():
    return Transaction(WebpayOptions(commerce_code, api_key, IntegrationType.TEST))