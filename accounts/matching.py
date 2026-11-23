"""Rule-based matching used for recommendations (SRS FR-12).

Version 1.0 deliberately uses simple, explainable rules: sector, stage and
location overlap. AI matching is out of scope for this release.
"""
from django.db.models import Q

from opportunities.models import Opportunity

from .models import User


def _tokens(value):
    return {part.strip().lower() for part in (value or "").replace(";", ",").split(",") if part.strip()}


def _overlaps(a, b):
    a, b = (a or "").lower(), (b or "").lower()
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    return bool(_tokens(a) & _tokens(b))


def _same_place(a, b):
    a_parts = _tokens(a) | {(a or "").lower().strip()}
    b_parts = _tokens(b) | {(b or "").lower().strip()}
    a_parts.discard("")
    b_parts.discard("")
    return bool(a_parts & b_parts)


def score_person(viewer, other):
    """Return (score, reasons) describing how well `other` matches `viewer`."""
    score, reasons = 0, []
    viewer_sector = viewer.sector_label
    other_text = " ".join(
        filter(None, [other.sector_label, other.mentor_expertise, other.bio, other.investor_type])
    )
    if viewer_sector and _overlaps(viewer_sector, other_text):
        score += 3
        reasons.append("Sector match")
    elif viewer.role != User.Role.ENTREPRENEUR and other.business_sector and _overlaps(
        other.business_sector, viewer.interest_sectors + " " + viewer.mentor_expertise
    ):
        score += 3
        reasons.append("Sector match")
    if viewer.business_stage and other.business_stage and viewer.business_stage.lower() == other.business_stage.lower():
        score += 2
        reasons.append("Same stage")
    if viewer.location and other.location and _same_place(viewer.location, other.location):
        score += 1
        reasons.append("Same location")
    if getattr(other, "is_verified", False):
        score += 1
        reasons.append("Verified")
    return score, reasons


def recommended_people(viewer, roles, limit=6):
    candidates = (
        User.objects.filter(is_active=True, is_staff=False, role__in=roles)
        .exclude(pk=viewer.pk)
    )
    ranked = []
    for person in candidates:
        score, reasons = score_person(viewer, person)
        if score > 0:
            person.match_score, person.match_reasons = score, reasons
            ranked.append(person)
    ranked.sort(key=lambda p: (-p.match_score, p.display_name.lower()))
    return ranked[:limit]


def recommended_opportunities(viewer, limit=4):
    sector = viewer.sector_label
    ranked = []
    for opportunity in Opportunity.visible():
        score, reasons = 0, []
        if sector and (_overlaps(sector, opportunity.sector) or (opportunity.sector or "").lower() == "all sectors"):
            score += 3
            reasons.append("Sector match")
        if viewer.location and opportunity.location and _same_place(viewer.location, opportunity.location):
            score += 1
            reasons.append("Location match")
        if score:
            opportunity.match_score, opportunity.match_reasons = score, reasons
            ranked.append(opportunity)
    ranked.sort(key=lambda o: (-o.match_score, o.deadline or o.created_at.date()))
    return ranked[:limit]


def search_people(queryset, query="", sector="", location="", stage=""):
    if query:
        queryset = queryset.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(username__icontains=query)
            | Q(organization__icontains=query)
            | Q(bio__icontains=query)
            | Q(business_name__icontains=query)
            | Q(business_description__icontains=query)
            | Q(mentor_expertise__icontains=query)
            | Q(investor_type__icontains=query)
        )
    if sector:
        queryset = queryset.filter(
            Q(business_sector__icontains=sector)
            | Q(interest_sectors__icontains=sector)
            | Q(mentor_expertise__icontains=sector)
        )
    if location:
        queryset = queryset.filter(location__icontains=location)
    if stage:
        queryset = queryset.filter(business_stage__icontains=stage)
    return queryset
