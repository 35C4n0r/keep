# ALERTS = {
#     "event_definition_id": "671a28a03696bb3801a7a9f1",
#     "event_definition_type": "aggregation-v1",
#     "event_definition_title": [
#         "EventDefinition - 1",
#         "EventDefinition - 2",
#         "EventDefinition - 3",
#     ],
#     "event_definition_description": [
#         "Description - add",
#         "Description - commit",
#         "Description - push",
#     ],
#     "job_definition_id": "671a97cc3696bb3801a846a6",
#     "job_trigger_id": "671b2a533696bb3801a889b4",
#     "event": {
#         "id": [
#             "01JB11TNPRN9F643SPPEKJTX1A",
#             "01JAZZJAKSNYB7J616GXCPJST2",
#             "01JAZZJAKS82TDZAE82E0WAENT",
#         ],
#         "event_definition_type": "aggregation-v1",
#         "event_definition_id": "671a28a03696bb3801a7a9f1",
#         "origin_context": "urn:graylog:message:es:graylog_0:abdb8110-9290-11ef-9a79-0242ac170004",
#         "timestamp": [
#             "2024-10-25T05:19:12.717Z",
#             "2024-9-25T05:19:12.717Z",
#             "2024-8-25T05:19:12.717Z",
#         ],
#         "timestamp_processing": "2024-10-25T05:19:15.672Z",
#         "timerange_start": None,
#         "timerange_end": None,
#         "streams": [],
#         "source_streams": ["000000000000000000000001"],
#         "message": "Event - 1",
#         "source": "server",
#         "key_tuple": [],
#         "key": "",
#         "priority": 3,
#         "scores": {},
#         "alert": True,
#         "fields": {},
#         "group_by_fields": {},
#         "replay_info": {
#             "timerange_start": "2024-10-24T05:19:14.706Z",
#             "timerange_end": "2024-10-25T05:19:14.706Z",
#             "query": [
#                 "source:172.23.0.1",
#             ],
#             "streams": ["000000000000000000000001"],
#             "filters": [],
#         },
#     },
#     "backlog": [],
# }


ALERTS = {
    "event_definition_id": "671a28a03696bb3801a7a9f1",
    "event_definition_type": "aggregation-v1",
    "event_definition_title": "Event - 1",
    "event_definition_description": ".",
    "job_definition_id": "671a97cc3696bb3801a846a6",
    "job_trigger_id": "671a9dfe3696bb3801a8536d",
    "event": {
        "id": "01JAZZJAKS82TDZAE82E0WAENT",
        "event_definition_type": "aggregation-v1",
        "event_definition_id": "671a28a03696bb3801a7a9f1",
        "origin_context": "urn:graylog:message:es:graylog_0:d0a9a7a0-91f1-11ef-9a79-0242ac170004",
        "timestamp": "2024-10-24T10:22:04.556Z",
        "timestamp_processing": "2024-10-24T19:20:30.585Z",
        "timerange_start": None,
        "timerange_end": None,
        "streams": [],
        "source_streams": ["000000000000000000000001"],
        "message": "Event - 1",
        "source": "server",
        "key_tuple": [],
        "key": "",
        "priority": 3,
        "scores": {},
        "alert": True,
        "fields": {},
        "group_by_fields": {},
        "replay_info": {
            "timerange_start": "2024-10-23T19:20:29.706Z",
            "timerange_end": "2024-10-24T19:20:29.706Z",
            "query": "source:172.23.0.1",
            "streams": ["000000000000000000000001"],
            "filters": [],
        },
    },
    "backlog": [],
}
