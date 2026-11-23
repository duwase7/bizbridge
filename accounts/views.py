from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm, SignUpForm
from .matching import recommended_opportunities, recommended_people, search_people
from .models import User


def home(request):
    return render(request, "home.html")


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your BizBridge account is ready.")
            return redirect("dashboard")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


@login_required
def dashboard(request):
    user = request.user
    if user.is_staff:
        return redirect("admin_dashboard")
    recommendation_roles = {
        User.Role.ENTREPRENEUR: (User.Role.MENTOR, User.Role.INVESTOR, User.Role.ENTREPRENEUR),
        User.Role.MENTOR: (User.Role.ENTREPRENEUR,),
        User.Role.INVESTOR: (User.Role.ENTREPRENEUR,),
    }.get(user.role, ())
    context = {
        "recommended_people": recommended_people(user, recommendation_roles) if not user.is_staff else [],
        "recommended_opportunities": recommended_opportunities(user) if not user.is_staff else [],
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("dashboard")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})


SEARCHABLE_ROLES = {
    User.Role.ENTREPRENEUR: (User.Role.MENTOR, User.Role.INVESTOR, User.Role.ENTREPRENEUR),
    User.Role.MENTOR: (User.Role.ENTREPRENEUR,),
    User.Role.INVESTOR: (User.Role.ENTREPRENEUR,),
}
BUSINESS_STAGES = ("Idea", "Early stage", "Start-up", "Growth", "Established")


def searchable_roles_for(user):
    if user.is_staff:
        return tuple(User.Role.values)
    return SEARCHABLE_ROLES.get(user.role, ())


@login_required
def people_directory(request):
    """Search and filter people (FR-10 entrepreneurs, FR-11 investors)."""
    allowed_roles = searchable_roles_for(request.user)
    selected_role = request.GET.get("role", "").strip()
    if selected_role not in allowed_roles:
        selected_role = ""
    filters = {
        "query": request.GET.get("q", "").strip(),
        "sector": request.GET.get("sector", "").strip(),
        "location": request.GET.get("location", "").strip(),
        "stage": request.GET.get("stage", "").strip(),
    }
    people = User.objects.filter(
        is_active=True,
        is_staff=False,
        role__in=[selected_role] if selected_role else allowed_roles,
    ).exclude(pk=request.user.pk)
    people = search_people(people, **filters).order_by("-is_verified", "first_name", "username")

    role_labels = dict(User.Role.choices)
    return render(
        request,
        "accounts/people.html",
        {
            "people": people,
            "role_options": [(role, role_labels[role]) for role in allowed_roles],
            "selected_role": selected_role,
            "stages": BUSINESS_STAGES,
            "has_filters": selected_role or any(filters.values()),
            **filters,
        },
    )


@login_required
def person_detail(request, user_id):
    """Full profile page reached from search results (FR-13)."""
    person = get_object_or_404(User, pk=user_id, is_active=True, is_staff=False)
    if person != request.user and person.role not in searchable_roles_for(request.user):
        messages.info(request, "That profile is not available for your role.")
        return redirect("people_directory")
    context = {"person": person}
    context.update(relationship_context(request.user, person))
    return render(request, "accounts/person_detail.html", context)


def relationship_context(viewer, person):
    """Request status between the viewer and a profile, used to pick action buttons."""
    from investor_connections.models import InvestorConnectionRequest
    from mentorships.models import MentorshipRequest

    from networking.models import Connection

    connection = Connection.between(viewer, person)
    context = {
        "connection": connection,
        "can_connect": person.role in searchable_roles_for(viewer)
        and (connection is None or connection.status == Connection.Status.DECLINED),
    }
    if viewer.role == User.Role.ENTREPRENEUR and person.role == User.Role.MENTOR:
        context["mentorship_request"] = MentorshipRequest.objects.filter(
            entrepreneur=viewer, mentor=person
        ).first()
    if viewer.role == User.Role.ENTREPRENEUR and person.role == User.Role.INVESTOR:
        context["investor_request"] = InvestorConnectionRequest.objects.filter(
            entrepreneur=viewer, investor=person
        ).first()
    return context
