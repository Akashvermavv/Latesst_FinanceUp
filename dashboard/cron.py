from .models import *
from django.db.models import Q,Sum,Avg


def adpack_daily_update():
	
	all_active_adpacks=bought_adpack.objects.filter(Q(expiration_date__gt=datetime.now()))

	for pack in all_active_adpacks:
		user=pack.user
		quantity=pack.total_quantity
		everyday_revenue=pack.everyday_revenue
		b=balance.objects.get(user=user)

		
		b.current_balance=round(float(b.current_balance+everyday_revenue),2)
		b.save()
		

		adpack_update.objects.create(bought_adpack_name=pack,today_revenue=everyday_revenue)