from django.contrib import admin

from dashboard.models import *
admin.site.register(deposit_history)
admin.site.register(balance)
admin.site.register(pm_accounts)
admin.site.register(InvestmentPlans)
admin.site.register(PartnershipPlans)
admin.site.register(PremiumPlan)
admin.site.register(PurchasedPackage)
admin.site.register(AllUserNotice)
admin.site.register(FranchiseWithdraw)
admin.site.register(withdraw_requests)
admin.site.register(DepositMoney)

admin.site.register(KycVerification)