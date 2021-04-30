from .models import *
from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=withdraw_requests) 
def create_profile(sender, instance, **kwargs):
	if instance.payment_error == True:

		b=balance.objects.get(user=instance.user)
		b.current_balance=round(float(b.current_balance+instance.amount),2)
		b.save()