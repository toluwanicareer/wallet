from django.shortcuts import render
from django.views import View
import json
from .models import test_model
from django.http import HttpResponse
from dash.models import tx_handler
from django.views.decorators.csrf import csrf_exempt
import pdb

# Create your views here.

@csrf_exempt
def handle_tx(request):
   test_model.objects.create(data=request.body)
   payload=request.body.decode("utf-8")

   notification_data = json.loads(payload)
   tx_hash=notification_data.get('hash')
   input_list=notification_data.get('inputs')[0].get('addresses')
   output_list=notification_data.get('outputs')[0].get('addresses')
   total=notification_data.get('total')

   tx_handler(tx_hash,input_list, output_list, total)
   return HttpResponse(status=200)