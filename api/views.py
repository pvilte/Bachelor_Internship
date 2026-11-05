from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse

from retrieve.retrieve import *
from record.record import *
from prov_format.generate_prov import generate_prov
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
class AllTraces(APIView):
    """
    View to retrieve all traces in the database.
    """

    # Document the optional query parameter for returning results either in PROV-O representation or JSON format:
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='type',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                default='default',
                enum=['default', 'prov'],
                description='Return the result in PROV-O by selecting "prov", or in JSON format by selecting "default"'
            )
        ]
    )

    def get(self, request):
        """
        Return the list of all traces either in JSON or PROV-O.
        """
        retrieval_type = request.query_params.get("type", "default")

        result = collect_all_traces()

        if retrieval_type == "prov":
            # Return generated PROV-O for the result:
            rdf_result = generate_prov("output")
            return HttpResponse(rdf_result.serialize(format="trig"), content_type="rdf")

        return Response(result)


class EventsWithAdapt(APIView):
    """
    View to retrieve all events with adaptations.
    """

    # Document the optional query parameter for returning results either in PROV-O representation or JSON format:
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='type',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                default='default',
                enum=['default', 'prov'],
                description='Return the result in PROV-O by selecting "prov", or in JSON format by selecting "default"'
            )
        ]
    )

    def get(self, request):
        """
        Return the list of all events with adaptations either in JSON or PROV-O.
        """
        retrieval_type = request.query_params.get("type", "default")

        result = all_events_with_adaptations()

        if retrieval_type == "prov":
            # Return generated PROV-O for the result:
            rdf_result = generate_prov("output")
            return HttpResponse(rdf_result.serialize(format="trig"), content_type="rdf")
        
        return Response(result)


class ReasonImpact(APIView):
    """
    View to retrieve reason, impact or both keys of adaptations.
    """
    def get(self, request, key):
        """
        Return the list of either reson, impact or both keys of adaptations.
        """
        result = reason_and_impact_keys_of_adaptation(key)
        return Response(result)


class SingleInstance(APIView):
    """
    View to retrieve trace by the instance ID.
    """

    # Document the optional query parameter for returning results either in PROV-O representation or JSON format:
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='type',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                default='default',
                enum=['default', 'prov'],
                description='Return the result in PROV-O by selecting "prov", or in JSON format by selecting "default"'
            )
        ]
    )

    def get(self, request, instance):
        """
        Return the trace of an Instance either in JSON or PROV-O:
        """
        retrieval_type = request.query_params.get("type", "default")

        result = collect_trace_based_on_instance_id(instance)

        if retrieval_type == "prov":
            # Return generated PROV-O for the result:
            rdf_result = generate_prov("output")
            return HttpResponse(rdf_result.serialize(format="trig"), content_type="rdf")
        
        return Response(result)


class ImpactOfInstance(APIView):
    """
    View to retrieve impact of an instance.
    """
    def get(self, request, instance):
        """
        Return the impact of instance:
        """
        result = collect_impact_of_instance(instance)
        return Response(result)


class TraceData(APIView):
    """
    View to record provenance data to database.
    """

    # Document the JSON request along with an example of how one should look like:
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                additional_properties=True,
            ),
            description="JSON data to record traces.",
            example=[
                {
                    "trace_attributes": {},
                    "events": [
                        {
                            "concept:name": "Submit loan application",
                            "processId": "loan-origination",
                            "instanceId": "Instance-76745",
                            "org:resource": "Resource-3929",
                            "time:timestamp": "2025-11-21 17:27:53.402660+00:00",
                        }
                    ],
                }
            ],
        ),
        # document the server responses and their descriptions:
        responses={
            201: 'Recording complete!', 
            500: 'Server error',
        },
    )

    def post(self, request):
        """
        Record the JSON data to Neo4j database:
        """
        # take the JSON data provided by user:
        data = request.data

        record_from_api(data)
        return Response("Recording complete!")


class ImpactData(APIView):
    """
    View to record overall impact of instance in database.
    """

    # Document the JSON request along with an example of how one should look like:
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                additional_properties=True,
            ),
            description="JSON data to record overall impact.",
            example=[
                {
                    "instance:id": "Instance-1234",
                    "impact:type": "",
                    "impact": "Process sped up",
                }
            ],
        ),
        # document the server responses and their descriptions:
        responses={
            200: 'Recording complete!', 
            500: 'Server error',
        },
    )   

    def put(self, request):
        """
        Record overall impact of instance in database:
        """
        # take the JSON data provided by user:
        data = request.data
        
        record_impact_from_api(data)
        return Response("Recording complete!")
