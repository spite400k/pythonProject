from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def coupon(request):
    if 'coupon_code' in request.GET:
        coupon_code = request.GET['coupon_code']
        if coupon_code == '0001':
            result = '1000円引きクーポン！'
        elif coupon_code == '0002':
            result = '10%引きクーポン！'
        else:
            result = 'Error:Not found coupon code!'
        return HttpResponse(result)