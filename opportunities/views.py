from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, render

from .models import Opportunity


@login_required
def opportunity_list(request):
    """Search and filter opportunities; expired ones are hidden (FR-10, FR-15)."""
    opportunities = Opportunity.visible()

    search_query = request.GET.get("q", "").strip()
    selected_category = request.GET.get("category", "").strip()
    sector = request.GET.get("sector", "").strip()
    location = request.GET.get("location", "").strip()

    if search_query:
        opportunities = opportunities.filter(
            Q(title__icontains=search_query)
            | Q(provider__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(sector__icontains=search_query)
            | Q(location__icontains=search_query)
        )
    if sector:
        opportunities = opportunities.filter(
            Q(sector__icontains=sector) | Q(sector__iexact="All sectors")
        )
    if location:
        opportunities = opportunities.filter(location__icontains=location)

    valid_categories = dict(Opportunity.Category.choices)
    if selected_category in valid_categories:
        opportunities = opportunities.filter(category=selected_category)
    else:
        selected_category = ""

    return render(
        request,
        "opportunities/list.html",
        {
            "opportunities": opportunities,
            "search_query": search_query,
            "selected_category": selected_category,
            "sector": sector,
            "location": location,
            "categories": Opportunity.Category.choices,
            "has_filters": any((search_query, selected_category, sector, location)),
        },
    )


@login_required
def opportunity_detail(request, pk):
    """Full opportunity page (FR-13); views feed the admin reports (FR-26)."""
    if request.user.is_staff:
        opportunity = get_object_or_404(Opportunity, pk=pk)
    else:
        opportunity = get_object_or_404(Opportunity.visible(), pk=pk)
        Opportunity.objects.filter(pk=pk).update(view_count=F("view_count") + 1)
    return render(request, "opportunities/detail.html", {"opportunity": opportunity})
