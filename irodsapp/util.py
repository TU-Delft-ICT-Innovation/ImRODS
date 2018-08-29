from django.core.mail import mail_admins
from .models import Error



def log_exception(error, e):
    mail_admins(error, str(e), fail_silently=True)
    error += ":" + str(e)
    print(error)    
    Error.objects.create(error=error)

def log_and_raise_exception(error, e):
    mail_admins(error, str(e), fail_silently=True)
    error += ":" + str(e)
    print(error)    
    Error.objects.create(error=error)
    raise Exception(e)  