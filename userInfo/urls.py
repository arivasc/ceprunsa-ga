from django.urls import path
from userInfo.userCeprunsaPersonalInfoViews import UserCeprunsaPersonalInfoListCreateView, UserCeprunsaPersonalInfoDetailView
from userInfo.userCeprunsaPaymentInfoViews import UserCeprunsaPaymentInfoListCreateView, UserCeprunsaPaymentInfoDetailView

urlpatterns = [
  path('personal-info', UserCeprunsaPersonalInfoListCreateView.as_view(), name='personal-info'),
  path('personal-info/<int:pk>', UserCeprunsaPersonalInfoDetailView.as_view(), name='personal-info-detail'),
  path('payment-info', UserCeprunsaPaymentInfoListCreateView.as_view(), name='payment-info'),
  path('payment-info/<int:pk>', UserCeprunsaPaymentInfoDetailView.as_view(), name='payment-info-detail'),
]
  