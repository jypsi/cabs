from django.shortcuts import get_object_or_404, Http404, render

from finance.models import Payment

from .utils import encrypt, decrypt


class CCAvenue(object):

    def __init__(self, config):
        self._project_name = config['PROJECT_NAME']
        self._gateway_base_url = config['GATEWAY_BASE_URL']
        self._merchant_id = config['MERCHANT_ID']
        self._access_code = config['ACCESS_CODE']
        self._working_key = config['WORKING_KEY']
        self._redirect_url = config['REDIRECT_URL']
        self._cancel_url = config['CANCEL_URL']
        self._billing_details = config['BILLING_DETAILS']
        self._language = config['LANGUAGE']

    def handle_start(self, request):
        invoice_id = request.GET.get('order_id')
        if not invoice_id:
            raise Http404

        payment = get_object_or_404(Payment, invoice_id=invoice_id)

        merchant_data = '&'.join([
            'merchant_id={}'.format(self._merchant_id),
            'order_id={}'.format(payment.invoice_id),
            'currency={}'.format(payment.amount.currency.code),
            'amount={}'.format(payment.amount.amount),
            'redirect_url={}'.format(self._redirect_url),
            'cancel_url={}'.format(self._cancel_url),
            'language={}'.format(self._language),
            'billing_name={}'.format(self._billing_details['NAME']),
            'billing_address={}'.format(self._billing_details['ADDRESS']),
            'billing_city={}'.format(self._billing_details['CITY']),
            'billing_state={}'.format(self._billing_details['STATE']),
            'billing_zip={}'.format(self._billing_details['ZIP']),
            'billing_country={}'.format(self._billing_details['COUNTRY']),
            'billing_tel={}'.format(self._billing_details['TEL']),
            'billing_email={}'.format(self._billing_details['EMAIL']),
            'delivery_name={}'.format(self._billing_details['NAME']),
            'delivery_address={}'.format(self._billing_details['ADDRESS']),
            'delivery_city={}'.format(self._billing_details['CITY']),
            'delivery_state={}'.format(self._billing_details['STATE']),
            'delivery_zip={}'.format(self._billing_details['ZIP']),
            'delivery_country={}'.format(self._billing_details['COUNTRY']),
            'delivery_tel={}'.format(self._billing_details['TEL']),
            'delivery_email={}'.format(self._billing_details['EMAIL']),
            'merchant_param1=',
            'merchant_param2=',
            'merchant_param3=',
            'merchant_param4=',
            'merchant_param5=',
            'integration_type=iframe_normal',
            'promo_code=',
            'customer_identifier='
        ])

        encrypted_merchant_data = encrypt(merchant_data, self._working_key)

        return render(request, 'finance/ccavenue/start.html', context={
            'project_name': self._project_name,
            'gateway_base_url': self._gateway_base_url,
            'merchant_id': self._merchant_id,
            'encrypted_data': encrypted_merchant_data,
            'access_code': self._access_code,
        })

    def handle_cancel(self, request):
        enc_resp = request.POST['encResp']
        resp = decrypt(enc_resp, self._working_key)
        return render(request, 'finance/ccavenue/cancel.html', context={'response': resp})

    def handle_success(self, request):
        enc_resp = request.POST['encResp']
        resp = decrypt(enc_resp, self._working_key)
        return render(request, 'finance/ccavenue/success.html', context={'response': resp})
