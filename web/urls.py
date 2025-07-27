from django.urls import path

from web.views import DashboardView, ChatView, ProfileUpdateView, CourseView, AdminReviewListView, AdminReviewTaskView, \
    AdminDashboardView, AdminStudentsView, AdminBoxesView, BoxApplicationView, AdminLectureList, AdminLectureEditView, \
    AdminLectureCreateView, AdminAllChatsView, AdminLectureDelete, get_part_of_messages

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("chat/<int:pk>/", ChatView.as_view(), name="chat"),
    path("chat_admin/<int:pk>/", ChatView.as_view(), name="admin_chat"),
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
    path("course/<int:pk>/", CourseView.as_view(), name="course"),
    path("admin_review_list/", AdminReviewListView.as_view(), name="admin_review_list"),
    path("admin_review_task/<int:pk>/", AdminReviewTaskView.as_view(), name="admin_review_task"),
    path("admin_dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("admin_students/", AdminStudentsView.as_view(), name="admin_students"),
    path("admin_boxes/", AdminBoxesView.as_view(), name="admin_boxes"),
    path("box_application/", BoxApplicationView.as_view(), name="box_application"),
    path("admin_lecture_list/", AdminLectureList.as_view(), name="admin_lecture_list"),
    path("admin_lecture_edit/<int:pk>/", AdminLectureEditView.as_view(), name="admin_lecture_edit"),
    path("admin_lecture_create/", AdminLectureCreateView.as_view(), name="admin_lecture_create"),
    path("admin_lecture_delete/<int:pk>/", AdminLectureDelete.as_view(), name="admin_lecture_delete"),
    path("admin_all_chats/", AdminAllChatsView.as_view(), name="admin_all_chats"),
    path("load_more_messages/<int:pk>/",  get_part_of_messages, name="load_more_messages")
]