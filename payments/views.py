from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MyCheckoutSerializer, MyWebhookSerializer
from orders.models import Order
import stripe

stripe.api_key = 'sk_test_51OpHX02KSoBXprSFsfySxza5p7jKrRon7cwtzbgISH9Ncud9e9gFdctQpDYdggKJNOtm72CkwUxDrCqUted52J2s00xkeM999J'

class CheckoutSessionView(CreateAPIView):
    serializer_class = MyCheckoutSerializer

    def get(self, request, *args, **kwargs):
        return Response({'error': 'GET method not allowed'}, status=status.HTTP_400_BAD_REQUEST)
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        if not order_id:
            return Response({'error': 'No order_id provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        line_items = []
        for item in order.items.all():
            line_items.append({
                'price_data': {
                    'currency': 'mxn',
                    'product_data': {
                        'name': item.product.name,
                    },
                    'unit_amount': int(item.product.price * 100),
                },
                'quantity': item.quantity,
            })

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                metadata={'order_id': order.id},
                mode='payment',
                success_url='https://example.com/success',
                cancel_url='https://example.com/cancel',
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'url': checkout_session.url}, status=status.HTTP_200_OK)
    
endpoint_secret = 'whsec_GmrHNH9oHuzOUIGWOrUm4iIczsn6PWg2'
    
class WebhookView(CreateAPIView):
    serializer_class = MyWebhookSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return Response({'error': 'GET method not allowed'}, status=status.HTTP_400_BAD_REQUEST)
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            order_id = session['metadata']['order_id']
            order = Order.objects.get(id=order_id)
            order.status = 'paid'
        return Response({'message': 'Success'}, status=status.HTTP_200_OK)
    