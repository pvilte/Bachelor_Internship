from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from retrieve.retrieve import *
from record.record import *
from prov_format import generate_prov

# Create your views here.
class AllTraces(APIView):
    def get(self, request):
        result = collect_all_traces()
        return Response(result)

class EventsWithAdapt(APIView):
    def get(self, request):
        result = all_events_with_adaptations()
        return Response(result)

class ReasonImpact(APIView):
    def get(self, request, key):
        result = reason_and_impact_keys_of_adaptation(key)
        return Response(result)

class SingleInstance(APIView):
    def get(self, request, instance):
        result = collect_trace_based_on_trace_id(instance)
        return Response(result)

class ImpactOfInstance(APIView):
    def get(self, request, instance):
        result = collect_impact_of_instance(instance)
        return Response(result)