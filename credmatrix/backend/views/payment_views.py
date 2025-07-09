from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from backend.models import Payment
import time

class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount') * 100
        currency = request.data.get('currency', 'INR')

        if not amount:
            return Response({"error": "Amount is required"}, status=400)


        data = {
            "amount": amount,
            "currency": currency,
            "receipt": f"receipt_{request.user.id}_{int(time.time())}"
        }
        order = settings.razorpay_client.order.create(data=data)

        Payment.objects.create(
            user=request.user,
            order_id=order['id'],
            amount=amount,
        )

        return Response({
            "order_id": order['id'],
            "amount": order['amount'],
            "currency": order['currency'],
            "key": settings.RAZORPAY_KEY_ID
        })


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_id = request.data.get('payment_id')
        order_id = request.data.get('order_id')
        signature = request.data.get('signature')

        if not all([payment_id, order_id, signature]):
            return Response({"error": "Missing required parameters"}, status=400)

        try:

            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            }
            settings.razorpay_client.utility.verify_payment_signature(params_dict)


            payment = Payment.objects.get(order_id=order_id)
            payment.payment_id = payment_id
            payment.status = 'completed'
            payment.save()

            return Response({"message": "Payment successful"})
        except Exception as e:
            return Response({"error": "Payment verification failed", "details": str(e)}, status=401)