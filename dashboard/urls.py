
from django.urls import path,include,re_path
from django.views.generic import TemplateView
from . import views



urlpatterns = [
	path('',views.dashboard,name='dashboard'),
	path('kyc_verification2',views.kyc_verification2,name='kyc_verification2'),
	path('kyc_verification_request',views.kyc_verification_request,name='kyc_verification_request'),
	path('kyc_verification_user_info',views.kyc_verification_user_info,name='kyc_verification_user_info'),
	path('deposit/',views.deposit_money,name='deposit'),
	path('franchise_deposit_request/',views.franchise_deposit_request,name='franchise_deposit_request'),
	path('franchise_deposit_request_rejected/',views.franchise_deposit_request_rejected,name='franchise_deposit_request_rejected'),
	path('franchise_deposit_request_approved/',views.franchise_deposit_request_approved,name='franchise_deposit_request_approved'),
	path('deposit_request/',views.deposit_request,name='deposit_request'),
	path('admin',views.admin_dashboard,name='admin_dashboard'),
	path('manage_user',views.manage_user,name='manage_user'),
	path('cal_charge',views.cal_charge,name='cal_charge'),
	path('test',views.test,name='test'),
	path('dfs_matching/',views.dfs_matching,name='dfs_matching'),
	path('add_fund/',views.add_fund,name='add_fund'),
	path('binary_tree/<int:pk>',views.binary_tree,name='binary_tree'),
	path('plans/',views.plans,name='plans'),
	path('all_user_notice/',views.all_user_notice,name='all_user_notice'),
	path('withdraw_pending/',views.withdraw_pending,name='withdraw_pending'),

	path('purchased_plans/',views.purchased_plans,name='purchased_plans'),
	path('ban_user/',views.ban_user,name='ban_user'),
	path('unban_user/',views.unban_user,name='unban_user'),
	# path('approve_withdraw_request/',views.approve_withdraw_request,name='approve_withdraw_request'),
	# path('reject_withdraw_request/',views.reject_withdraw_request,name='reject_withdraw_request'),


	path('add_premium_plan/',views.add_premium_plan,name='add_premium_plan'),
	path('premium_plan_success/',views.premium_plan_success,name='premium_plan_success'),

	path('payment_success/',views.payment_success,name='payment_success'),
	path('payment_failed/',views.payment_failed,name='payment_failed'),
	path('payment_status/',views.payment_status,name='payment_status'),
	# path('send_money/',TemplateView.as_view(template_name='dashboard/send-fund.html'),name='send_money'),
	path('send_money/',views.send_money,name='send_money'),
	path('admin_send_money/',views.admin_send_money,name='admin_send_money'),
	path('balance_transfer/',views.balance_transfer,name='balance_transfer'),
	path('admin_balance_transfer/',views.admin_balance_transfer,name='admin_balance_transfer'),
	path('adpack_list/',views.adpack_list,name='adpack_list'),
	path('refer/',views.refer_page,name='refer'),
	path('buy_adpack/<int:level>/',views.buy_adpack,name='buy_adpack'),
	path('refer_list/',views.refer_list,name='refer_list'),
	path('revenue_history/',views.revenue_history,name='revenue_history'),
	path('adpack_history/',views.adpack_history,name='adpack_history'),
	path('personal_info/',views.personal_info,name='personal_info_update'),
	path('payment_info/',views.payment_info,name='payment_info'),
	path('pm_add/',views.pm_add,name='pm_add'),
	path('agent_account_add/',views.agent_account_add,name='agent_account_add'),
	path('bank_info_add/',views.bank_info_add,name='bank_info_add'),
	path('withdraw/',views.withdraw,name='withdraw'),
	path('franchise_withdraw/',views.franchise_withdraw,name='franchise_withdraw'),
	path('franchise_request/',views.franchise_request,name='franchise_request'),
	path('franchise_request_rejected/',views.franchise_request_rejected,name='franchise_request_rejected'),
	path('franchise_request_approved/',views.franchise_request_approved,name='franchise_request_approved'),
	path('withdraw_request/',views.withdraw_request,name='withdraw_request'),
	path('withdraw_request_premium/',views.withdraw_request_premium,name='withdraw_request_premium'),
	path('change_password/',views.change_password,name='change_password'),
	path('withdraw_history/',views.withdraw_history,name='withdraw_history'),
	path('deposits_history/',views.deposits_history,name='deposits_history'),
	path('sendmoney_history/',views.send_Money_history,name='sendmoney_history'),
	path('receivedmoney_history/',views.receivedmoney_history,name='receivedmoney_history'),
	path('bkash_add/',views.bkash_add,name='bkash_add'),
	path('rocket_add/',views.rocket_add,name='rocket_add'),
	path('nagad_add/',views.nagad_add,name='nagad_add'),
	path('payment_gateway/',views.payment_gateway,name='payment_gateway'),

	]
    
