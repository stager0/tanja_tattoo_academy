from django.urls import path
from django.views.generic import TemplateView

from web.views import DashboardView

urlpatterns = [
    path("thank_you/", TemplateView.as_view(template_name="thank-you.html"), name="thank_you"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("chat/", TemplateView.as_view(template_name="chat.html"), name="chat"),
    path("profile/", TemplateView.as_view(template_name="profile.html"), name="profile"),
    path("course/", TemplateView.as_view(template_name="course.html"), name="course"),
    path("admin_review_list/", TemplateView.as_view(template_name="admin-review-list.html"), name="admin_review_list"),
    path("admin_review_task/", TemplateView.as_view(template_name="admin-review-task.html"), name="admin_review_task"),
    path("admin_dashboard/", TemplateView.as_view(template_name="admin-dashboard.html"), name="admin_dashboard"),
    path("admin_students/", TemplateView.as_view(template_name="admin-students.html"), name="admin_students"),
    path("admin_boxes/", TemplateView.as_view(template_name="admin-boxes.html"), name="admin_boxes"),
    path("box_application/", TemplateView.as_view(template_name="box-application.html"), name="box_application"),
    path("admin_lecture_list/", TemplateView.as_view(template_name="admin-lecture-list.html"), name="admin_lecture_list"),
    path("admin_lecture_edit/", TemplateView.as_view(template_name="admin-lecture-edit.html"), name="admin_lecture_edit"),
    path("admin_lecture_create/", TemplateView.as_view(template_name="admin-lecture-create.html"), name="admin_lecture_create"),
    path("admin_all_chats/", TemplateView.as_view(template_name="admin-all-chats.html"), name="admin_all_chats")
]