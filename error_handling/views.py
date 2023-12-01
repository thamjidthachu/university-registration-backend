from django.shortcuts import render


# HTTP Error 400
def handler400(request, exception):
    link = request.headers['host']
    if "my.um.edu.sa" in link:
        return render(request, "error400.html", {'host': "https://" + link})
    else:
        return render(request, "error400.html", {'host': "http://" + link})


# HTTP Error 403
def handler403(request, exception):
    link = request.headers['host']
    if "my.um.edu.sa" in link:

        return render(request, "error403.html", {'host': "https://" + link})
    else:
        return render(request, "error403.html", {'host': "http://" + link})


# HTTP Error 404
def handler404(request, exception):
    link = request.headers['host']
    if "my.um.edu.sa" in link:
        return render(request, "error404.html", {'host': "https://" + link})
    else:
        return render(request, "error404.html", {'host': "http://" + link})


# HTTP Error 500
def handler500(request):
    link = request.headers['host']
    if "my.um.edu.sa" in link:
        return render(request, "error500.html", {'host': "https://" + link})
    else:
        return render(request, "error500.html", {'host': "http://" + link})
