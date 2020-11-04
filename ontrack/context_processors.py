import os


def export_env_vars(request):
    data = {}
    data["HEROKU"] = os.getenv("HEROKU")
    return data
