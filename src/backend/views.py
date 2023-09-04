import json

from django.http import HttpResponse
from django.db import transaction
from datetime import datetime
import pytz
from django.http import JsonResponse
from .models import User, Software, Bug, BugVote
from django.views.decorators.csrf import csrf_exempt


def get_software_bugs(request, software_id):
    software = Software.objects.filter(id=software_id).first()
    if software is None:
        data = {
            "error": "SoftwareNotFound",
            "payload": []
        }
    else:
        status = request.GET.get("status", "")
        if status not in ["NEW", "CONFIRMED", "FIXED", "EXPECTED", "PROPOSAL", "DROPPED"]:
            bug_query = Bug.objects.filter(software=software)
        else:
            bug_query = Bug.objects.filter(software=software, status=status)
        bugs = bug_query.order_by("-updated_at").values()

        data = {
            "payload": list(bugs[0:20])
        }
    return JsonResponse(data)

@csrf_exempt
def post_bug_add(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            if "software" not in payload or payload["software"] == "":
                return JsonResponse({"error": "SoftwareIsNull"})
            software = Software.objects.filter(id=payload["software"]).first()
            if software is None:
                return JsonResponse({"error": "SoftwareCodeInvalid"})
            if "title" not in payload or payload["title"] == "":
                return JsonResponse({"error": "TitleIsNull"})
            if "description" not in payload or payload["description"] == "":
                return JsonResponse({"error": "DescriptionIsNull"})
            user = User.objects.filter(id=1).first()
            bug = Bug(user=user, software=software, title=payload["title"], description=payload["description"],
                      status="NEW", rating_total="2", rating_count="1", created_at=datetime.now(tz=pytz.UTC),
                      updated_at=datetime.now(tz=pytz.UTC))
            bug.save()
            bug_vote = BugVote(user=user, bug=bug, rating=2)
            bug_vote.save()
            if user is None:
                return JsonResponse({"error": "ServerErrorNullUser"})
            return JsonResponse({
                "payload": {
                    "id": bug.id
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "InvalidJSONPayload"})
    else:
        return JsonResponse({
            "error": "WrongHTTPMethod"
        })


def get_bug_details(request, bug_id):
    bug = Bug.objects.filter(id=bug_id).first()
    if bug is None:
        return JsonResponse({
            "error": "BugNotFound",
            "payload": None
        })
    else:
        return JsonResponse({"payload": {
            "id": bug.id,
            "user": {
                "id": bug.user.id,
                "username": bug.user.username
            },
            "title": bug.title,
            "status": bug.status,
            "description": bug.description,
            "rating_total": bug.rating_total,
            "rating_count": bug.rating_count,
            "created_at": bug.created_at,
            "updated_at": bug.updated_at
        }})


@csrf_exempt
def get_bug_vote(request, bug_id):
    user = User.objects.filter(id=1).first()
    if user is None:
        return JsonResponse({"error": "NoUser"})
    bug = Bug.objects.filter(id=bug_id).first()
    if bug is None:
        return JsonResponse({"error": "NoBug"})
    bug_vote = BugVote.objects.filter(user=user, bug=bug).first()

    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            if "vote" not in payload:
                return JsonResponse({"error": "NoVoteInPayload"})
            if payload["vote"] not in ["1", "2", "3", "4", "5"]:
                return JsonResponse({"error": "VoteValueInvalid"})
            if bug_vote is None:
                bug_vote = BugVote.objects.create(user=user, bug=bug, rating=int(payload["vote"]))
                bug.rating_count += 1
                bug.rating_total += bug_vote.rating
            else:
                bug.rating_total -= bug_vote.rating
                bug_vote.rating = int(payload["vote"])
                bug.rating_total += bug_vote.rating
            bug.save()
            bug_vote.save()
            return get_bug_details(request, bug_id)
        except json.JSONDecodeError:
            return JsonResponse({"error": "InvalidJSONPayload"})

    else:
        if bug_vote is None:
            return JsonResponse({"payload": 0})
        else:
            return JsonResponse({"payload": bug_vote.rating})


