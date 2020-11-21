import uuid

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse

from saleor.payment.interface import GatewayConfig, GatewayResponse, PaymentData, \
    PaymentMethodInfo, TokenConfig
from saleor.plugins.base_plugin import BasePlugin, ConfigurationTypeField
from saleor.payment.gateways.utils import get_supported_currencies
from saleor.payment import TransactionKind

GATEWAY_NAME = "Asseco EST"


class AssecoEST(BasePlugin):
    PLUGIN_NAME = GATEWAY_NAME
    PLUGIN_ID = "asseco_est"
    DEFAULT_ACTIVE = True
    DEFAULT_CONFIGURATION = [
        {"name": "Merchant ID", "value": "400000200"},
        {"name": "3D Key", "value": "TRPS0200"},
        {"name": "3D URL",
         "value": "https://entegrasyon.asseco-see.com.tr/fim/est3Dgate"},
        {"name": "Store customers card", "value": True},
        {"name": "Automatic payment capture", "value": True},
        {"name": "Supported currencies", "value": ""},
    ]

    CONFIG_STRUCTURE = {
        "Merchant ID": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Provide Merchant ID as given by your bank.",
            "label": "Merchant ID",
        },
        "3D Key": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Provide the 3D Secure key as given by your bank.",
            "label": "3D Key",
        },
        "3D URL": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "3D Secure URL for your bank.",
            "label": "3D URL",
        },
        "Store customers card": {
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": "Determines if Saleor should store cards on payments "
                         "in Stripe customer.",
            "label": "Store customers card",
        },
        "Automatic payment capture": {
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": "Determines if Saleor should automaticaly capture payments.",
            "label": "Automatic payment capture",
        },
        "Supported currencies": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Determines currencies supported by gateway."
                         " Please enter currency codes separated by a comma.",
            "label": "Supported currencies",
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configuration = {item["name"]: item["value"] for item in self.configuration}
        self.config = GatewayConfig(
            gateway_name=GATEWAY_NAME,
            auto_capture=configuration["Automatic payment capture"],
            supported_currencies=configuration["Supported currencies"],
            connection_params={
                "merchant_id": configuration["Merchant ID"],
                "3d_key": configuration["3D Key"],
            },
            store_customer=configuration["Store customers card"],
        )

    def webhook(self, request: WSGIRequest, path: str, previous_value) -> HttpResponse:
        # check if plugin is active
        # check signatures and headers.
        if path == '/webhook/successful':
            return JsonResponse(data={"paid": True})
        if path == '/webhook/failed':
            return JsonResponse(data={"paid": False})
        return HttpResponseNotFound()

    def process_payment(
            self, payment_information: PaymentData, previous_value
    ) -> GatewayResponse:
        return GatewayResponse(
            is_success=True,
            action_required=False,
            kind=TransactionKind.CAPTURE,
            amount=payment_information.amount,
            currency=payment_information.currency,
            transaction_id=payment_information.token,
            error=None,
            payment_method_info=PaymentMethodInfo(
                last_4="1234",
                exp_year=2222,
                exp_month=12,
                brand="dummy_visa",
                name="Holder name",
                type="card",
            ),
        )

    def get_client_token(self, token_config: TokenConfig, previous_value):
        return str(uuid.uuid4())

    def get_supported_currencies(self, previous_value):
        return get_supported_currencies(self.config, GATEWAY_NAME)

    def get_payment_config(self, previous_value):
        return [{"field": "store_customer_card", "value": self.config.store_customer}]
