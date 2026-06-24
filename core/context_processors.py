from .models import Profile


def site_profile(request):
    profile = Profile.objects.first()
    return {'site_profile': profile}
