from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from .models import Opportunity


@login_required
def opportunity_list(request):
    opportunities = Opportunity.objects.filter(is_active=True)

    search_query = request.GET.get("q", "").strip()
    selected_category = request.GET.get("category", "").strip()

    if search_query:
        opportunities = opportunities.filter(
            Q(title__icontains=search_query)
            | Q(provider__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(sector__icontains=search_query)
            | Q(location__icontains=search_query)
        )

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
            "categories": Opportunity.Category.choices,
        },
    )
