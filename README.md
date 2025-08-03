# Tanja Tattoo / GodArt Tattoo - Full Stack Training Platform

![Tanja Tattoo Academy](media/readme_images/logo.jpg) 

**Tanja Tattoo / GodArt Tattoo** is a comprehensive, production-ready Full Stack platform for online tattoo art training. This project provides an immersive and interactive learning experience for students, complemented by a powerful, custom-built administrative panel that gives the mentor complete control over the educational content, student management, and overall platform operations.

The platform was developed with a strong focus on high-quality UI/UX, robust performance through optimized database queries, and the automation of routine tasks to create a seamless experience for both students and administrators.

Over 200 hours were invested in this project. It was made with passion.

## ✨ Core Philosophy

* **User-Centric Design:** Every feature, from the sales funnel to the learning dashboard, is designed to be intuitive and engaging.
* **Automation & Efficiency:** Repetitive tasks, such as sending notifications and updating statuses, are fully automated to allow the mentor to focus on teaching, not administration.
* **Performance First:** Database interactions are carefully optimized using advanced Django ORM techniques to ensure a fast and responsive experience, even with a large number of users and lessons.
* **Seamless Integration:** The platform tightly integrates with external services like Stripe, Telegram, and Mailjet to create a unified and professional ecosystem.

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| **Backend** | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) ![Django ORM](https://img.shields.io/badge/Django-ORM-092E20?style=for-the-badge&logo=django&logoColor=white) |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white) |
| **Authentication** | Custom `User` model (email-based, no `username`) |
| **APIs & Webhooks**| ![Stripe](https://img.shields.io/badge/Stripe-626CD9?style=for-the-badge&logo=stripe&logoColor=white) ![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white) ![Mailjet](https://img.shields.io/badge/Mailjet-000000?style=for-the-badge&logo=mailjet&logoColor=white) |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) |
| **Deployment** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white) ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white) |
| **Testing** | ![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white) (600+ lines) |
| **Additional** | Custom Middleware for error handling (404, 500) |

## 🚀 Key Features

### I. Public Section & Sales Funnel

1.  **Sales Landing Page (`index`)**
    * A comprehensive, multi-section landing page designed to convert visitors into students.
    * A dynamic pricing section with three tiers, featuring interactive modal windows for detailed plan comparison.
    * Full integration with the **Stripe** payment gateway.
    * A robust **Stripe Webhook** endpoint handles successful payments by automatically generating a unique subscription code and delivering it to the customer via **Mailjet API**.
    * A contact form that sends inquiries directly to the mentor's **Telegram** for a swift response.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Homepage Section 1](media/readme_images/index_1.jpg)
    ![Homepage Section 2](media/readme_images/index_2.jpg)
    ![Homepage Section 3](media/readme_images/index_3.jpg)
    ![Homepage Section 4](media/readme_images/index_4.jpg)
    ![Homepage Section 5](media/readme_images/index_5.jpg)
    ![Homepage Section 6](media/readme_images/index_6.jpg)
    ![Homepage Section 7](media/readme_images/index_7.jpg)
    ![Homepage Section 8](media/readme_images/index_8.jpg)
    ![Pricing Tiers](media/readme_images/index_tiers.jpg)
    ![Tier Details Modal](media/readme_images/index_tarif.jpg)
    ![Stripe Checkout Page](media/readme_images/stripe.jpg)
    ![Subscription Code Email](media/readme_images/stripe-email.jpg)
    ![Telegram Notification from Contact Form](media/readme_images/telegram-form.jpg)
    </details>

2.  **Authentication System**
    * Custom-built, secure pages for login, registration, and password recovery.
    * Registration is streamlined, using the purchased subscription code for validation.
    * New users receive a welcome email via **Mailjet API** and a welcome message in **Telegram**.
    * A secure password recovery flow sends a 6-digit code to the user's email, with **Telegram** notifications for password changes.

    <details>
    <summary>🖼️ View Screenshots</summary>
    
    ![Login Page](media/readme_images/login.jpg)
    ![Registration Page](media/readme_images/register.jpg)
    ![Welcome Email](media/readme_images/welcome_email.jpg)
    ![Welcome Telegram Notification](media/readme_images/telegram-user-registered.jpg)
    ![Forgot Password Page](media/readme_images/forgot-password.jpg)
    ![Success Request Page](media/readme_images/forgot-password-sent.jpg)
    ![Recovery Code Email](media/readme_images/forgot-password-email.jpg)
    ![Reset Password Form](media/readme_images/forgot-password-form.jpg)
    ![Reset Password Success](media/readme_images/forgot-password-success.jpg)
    ![Telegram Password Change Notification](media/readme_images/telegram-change-password.jpg)
    </details>

### II. Student Platform

3.  **Dashboard**
    * A central hub for students, featuring a dynamic progress bar calculated based on approved homework.
    * Real-time notifications for unread chat messages.
    * A "Continue Learning" button that intelligently directs the user to their next uncompleted lesson.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Student Dashboard](media/readme_images/dashboard.jpg)
    </details>

4.  **Course Page**
    * An interactive lesson list with pagination and clear visual statuses: "Completed" (✅), "Pending Review" (⏳), and "Locked" (⚪).
    * Each lesson includes a video, a detailed text lecture, and a homework assignment.
    * A submission form allows students to upload photos and add comments for their assignments. The form is automatically disabled after submission to prevent duplicate entries.
    * **Telegram** notifications are sent to the student (confirming submission) and the mentor (alerting to a new review).

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Course Page View 1](media/readme_images/my_course.jpg)
    ![Course Page View 2](media/readme_images/my_course1.jpg)
    ![Mentor's Telegram Notification for New Homework](media/readme_images/telegram-homework.jpg)
    </details>

5.  **Start Box Application**
    * An exclusive feature for "Pro" and "Master" tier students.
    * A one-time application form for a physical tattoo starter kit.
    * The system intelligently disables the form after the first submission and pre-fills it with the submitted data for reference.
    * A fully automated **Telegram** notification workflow keeps both student and mentor updated on the application and shipping status.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Box Application Page](media/readme_images/box-application.jpg)
    ![Box Application Success Modal](media/readme_images/box-application-success.jpg)
    ![Box Application Already Sent View](media/readme_images/box-application-sent.jpg)
    ![Mentor's Telegram Notification for New Application](media/readme_images/telegram-box-application.jpg)
    ![Student's Telegram Notification of Application Receipt](media/readme_images/telegram-box-application-user.jpg)
    </details>

6.  **Chat with Mentor**
    * A real-time chat interface with support for text messages and image uploads.
    * An efficient "Load Previous" button for message history pagination.
    * Unread message counters in the header and sidebar ensure users never miss a message.
    * **Telegram** notifications for all new messages to ensure instant communication.

    <details>
    <summary>🖼️ View Screenshots</summary>
    
    ![Student Chat Page](media/readme_images/chat.jpg)
    ![Student's Telegram Notification](media/readme_images/telegram-chat.jpg)
    ![Mentor's Telegram Notification](media/readme_images/telegram-chat-admin.jpg)
    </details>

7.  **User Profile**
    * A dedicated page for users to update their personal information (name, phone, email, avatar) and securely change their password.
    
    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Profile Page](media/readme_images/profile.jpg)
    </details>

### III. Custom Admin Panel for Mentor

8.  **Mentor Dashboard**
    * An "at-a-glance" dashboard summarizing the most critical information: pending homework, recent unread messages, and widgets for the highest and lowest student progress.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Mentor Dashboard](media/readme_images/mentor-dashboard.jpg)
    </details>

9.  **Homework Review Workflow**
    * A dedicated section to manage all student submissions with filters for "Pending," "Approved," and "All."
    * A detailed review page where the mentor can view the student's photo and comments, provide feedback, and either "Approve" or "Reject" the work.
    * This action triggers an automated notification to the student via the platform chat and **Telegram**, including the mentor's feedback.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Homework Review List](media/readme_images/tasks-list.jpg)
    ![Detailed Review Page](media/readme_images/tasks-detail.jpg)
    ![Homework Submission Notification to Admin](media/readme_images/telegram-tasks-detail-admin.jpg)
    ![Homework Approval Notification to User](media/readme_images/user-telegram-tasks.jpg)
    ![Homework Rejection Notification to User](media/readme_images/tasks-detail_1.jpg)
    ![Platform Chat Notification after Review](media/readme_images/user-task-review-chat.jpg)
    </details>

10. **Chat Management**
    * A centralized list of all student chats, sorted by recent activity and unread message count.
    * Includes a search filter to quickly find a student by name or email.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Admin Chat List](media/readme_images/admin-all-chats.jpg)
    </details>

11. **Lecture Management (CRUD)**
    * Full CRUD (Create, Read, Update, Delete) functionality for course lectures.
    * A robust **positional number system** allows the mentor to easily reorder lessons without being dependent on database primary keys.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Lecture List](media/readme_images/lecture-list.jpg)
    ![Edit Lecture](media/readme_images/lecture-edit.jpg)
    ![Delete Lecture Confirmation](media/readme_images/lecture-delete.jpg)
    ![Create Lecture](media/readme_images/lecture-create.jpg)
    </details>

12. **Student List**
    * A comprehensive overview of all students, displaying their progress, tier, and last activity.
    * Features two switchable view modes (grid and list) and advanced filters for progress and search queries.

    <details>
    <summary>🖼️ View Screenshots</summary>
    
    ![Student List (Grid View)](media/readme_images/students-list.jpg)
    ![Student List (List View)](media/readme_images/students-list_1.jpg)
    </details>

13. **Start Box Application Management**
    * A queue for managing starter kit applications with "Pending" and "Sent" filters.
    * A "Mark as Sent" button that automates the notification process to the student.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Box Application List](media/readme_images/box-application-list.jpg)
    </details>

### IV. Additional Pages & Architectural Highlights

* **Custom Error Pages:** Beautifully designed pages for 404, 500, and other HTTP errors, handled by custom middleware.
* **Payment Status Pages:** Themed pages for successful, canceled, and failed payments to maintain a consistent user experience.
* **Database Optimization:** All database queries are highly optimized using `select_related`, `prefetch_related`, and advanced annotation techniques (`Subquery`, `Count`) to ensure maximum performance.
* **Custom Validation:** Forms include custom validation logic to ensure data integrity and provide helpful user feedback.

<details>
<summary>🖼️ View Screenshots</summary>

![Success Pay Page](media/readme_images/success_pay.jpg)
![Cancel Pay Page](media/readme_images/cancel-pay.jpg)
![Error Pay Page](media/readme_images/error_pay.jpg)
![404 Page](media/readme_images/404.jpg)
![500 Page](media/readme_images/500.jpg)
</details>

## 🚀 Installation & Launch

1.  **Configure Environment Variables:**
    Create a `.env` file in the project root and fill in all required variables (API keys, database settings, `NGROK_AUTHTOKEN`, etc.).

2.  **Build the Docker Image:**
    ```bash
    docker build -t tanja-tattoo-app .
    ```

3.  **Run the Container:**
    Pass the environment variables from your local `.env` file to the container for a seamless startup.
    ```bash
    docker run --env-file .env -p 8000:8000 tanja-tattoo-app
    ```

## 🧪 Testing

The project is extensively covered by over **600 lines of tests** using the **Pytest** framework, ensuring the reliability and stability of all key application features and business logic.

```bash
    pytest
```
