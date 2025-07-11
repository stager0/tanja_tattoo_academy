from django.urls import path
from django.views.generic import TemplateView

from web.views import DashboardView, ChatView, ProfileView, CourseView, AdminReviewListView, AdminReviewTaskView, \
    AdminDashboardView, AdminStudentsView, AdminBoxesView, BoxApplicationView, AdminLectureList, AdminLectureEditView, \
    AdminLectureCreateView, AdminAllChatsView

urlpatterns = [
    path("thank_you/", TemplateView.as_view(template_name="thank-you.html"), name="thank_you"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("chat/", ChatView.as_view(), name="chat"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("course/", CourseView.as_view(), name="course"),
    path("admin_review_list/", AdminReviewListView.as_view(), name="admin_review_list"),
    path("admin_review_task/", AdminReviewTaskView.as_view(), name="admin_review_task"),
    path("admin_dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("admin_students/", AdminStudentsView.as_view(), name="admin_students"),
    path("admin_boxes/", AdminBoxesView.as_view(), name="admin_boxes"),
    path("box_application/", BoxApplicationView.as_view(), name="box_application"),
    path("admin_lecture_list/", AdminLectureList.as_view(), name="admin_lecture_list"),
    path("admin_lecture_edit/", AdminLectureEditView.as_view(), name="admin_lecture_edit"),
    path("admin_lecture_create/", AdminLectureCreateView.as_view(), name="admin_lecture_create"),
    path("admin_all_chats/", AdminAllChatsView.as_view(), name="admin_all_chats")
]