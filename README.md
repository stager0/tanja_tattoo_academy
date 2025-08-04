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

| Category          | Technology                                                                                                                                                                                                                                                                                                                      |
| :---------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Backend** | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) ![Django ORM](https://img.shields.io/badge/Django-ORM-092E20?style=for-the-badge&logo=django&logoColor=white) |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)                                                                                                         |
| **Authentication**| Custom `User` model (email-based, no `username`)                                                                                                                                                                                                                                                                                |
| **APIs & Webhooks**| ![Stripe](https://img.shields.io/badge/Stripe-626CD9?style=for-the-badge&logo=stripe&logoColor=white) ![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white) ![Mailjet](https://img.shields.io/badge/Mailjet-000000?style=for-the-badge&logo=mailjet&logoColor=white)   |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)         |
| **Deployment** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white) ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)         |
| **Testing** | ![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white) (600+ lines)                                                                                                                                                                                                               |
| **Additional** | Custom Middleware for error handling (404, 500)                                                                                                                                                                                                                                                                                 |

## 🏛️ Architectural Highlights & Key Logic

This project incorporates several advanced backend features to ensure robustness, scalability, and a superior user experience:

* **Custom User Model & Avatars:** The platform utilizes a custom Django User model that replaces the default `username` with `email` for a modern authentication experience. Users have the ability to upload and manage their own personal avatars.
* **Positional Numbering for Lectures:** To avoid issues with deleted objects and non-sequential primary keys, all lectures are ordered using a dedicated `position_number` field. This allows the mentor to easily and reliably reorder lessons at any time.
* **Automatic `last_activity` Tracking:** Custom middleware automatically updates a `last_activity` timestamp for a user with every request, allowing the mentor to see who is active on the platform.
* **Smart Chat System:** The chat leverages `is_read_user` and `is_read_admin` boolean flags on each message. This powers the real-time unread message counters and ensures that notifications are sent only when necessary.

## 🧪 Database Diagram

![Database Diagram](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326036/tanja_tattoo_diagram_c9kukr.png)

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

    ![Homepage Section 1](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326028/index_1_i40vmu.jpg)
    ![Homepage Section 2](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326028/index_2_czjjay.jpg)
    ![Homepage Section 3](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326028/index_3_zjtifq.jpg)
    ![Homepage Section 4](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326029/index_4_muq9qn.jpg)
    ![Homepage Section 5](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326029/index_5_qnmkrw.jpg)
    ![Homepage Section 6](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326029/index_6_hetny6.jpg)
    ![Homepage Section 7](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326030/index_7_o0umb9.jpg)
    ![Homepage Section 8](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326030/index_8_mbuacg.jpg)
    ![Pricing Tiers](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326031/index_tiers_vlmaj0.jpg)
    ![Tier Details Modal](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326030/index_tarif_tfooou.jpg)
    ![Stripe Checkout Page](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326035/stripe_wiuvzc.jpg)
    ![Subscription Code Email](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326035/stripe-email_ucj8px.png)
    ![Telegram Notification from Contact Form](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326044/telegram-form_tspjhz.png)
    </details>

2.  **Authentication System**
    * Custom-built, secure pages for login, registration, and password recovery.
    * Registration is streamlined, using the purchased subscription code for validation.
    * New users receive a welcome email via **Mailjet API** and a welcome message in **Telegram**.
    * A secure password recovery flow sends a 6-digit code to the user's email, with **Telegram** notifications for password changes.

    <details>
    <summary>🖼️ View Screenshots</summary>
    
    ![Login Page](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326032/login_urgbwp.png)
    ![Registration Page](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326037/register_i9obeu.png)
    ![Welcome Email](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326045/welcome_email_lcnufe.png)
    ![Welcome Telegram Notification](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326044/telegram-user-registered_ch48h2.png)
    ![Forgot Password Page](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326027/forgot-password_pjy8dl.jpg)
    ![Success Request Page](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326027/forgot-password-sent_urwopx.jpg)
    ![Recovery Code Email](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326026/forgot-password-email_wylrat.png)
    ![Reset Password Form](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326027/forgot-password-form_fhvxm2.jpg)
    ![Reset Password Success](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326027/forgot-password-success_biw7nd.jpg)
    ![Telegram Password Change Notification](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326038/telegram-change-password_bf7kn0.png)
    </details>

### II. Student Platform

3.  **Dashboard**
    * A central hub for students, featuring a dynamic progress bar calculated based on approved homework.
    * Real-time notifications for unread chat messages.
    * A "Continue Learning" button that intelligently directs the user to their next uncompleted lesson.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Student Dashboard](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326026/dashboard_xv3jql.jpg)
    </details>

4.  **Course Page**
    * An interactive lesson list with pagination and clear visual statuses: "Completed" (✅), "Pending Review" (⏳), and "Locked" (⚪).
    * Each lesson page includes a video, a detailed text lecture, and a homework assignment.
    * A submission form allows students to upload photos and add comments for their assignments. The form is automatically disabled after submission to prevent duplicate entries.
    * **Telegram** notifications are sent to the student (confirming submission) and the mentor (alerting to a new review).

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Course Page View 1](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326033/my_course_ap3aws.jpg)
    ![Course Page View 2](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326033/my_course1_alyvsz.jpg)
    ![Mentor's Telegram Notification for New Homework](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326044/telegram-homework_frl7ef.png)
    </details>

5.  **Start Box Application**
    * An exclusive feature for "Pro" and "Master" tier students.
    * A one-time application form for a physical tattoo starter kit.
    * The system intelligently disables the form after the first submission and pre-fills it with the submitted data for reference.
    * A fully automated **Telegram** notification workflow keeps both student and mentor updated on the application and shipping status.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Box Application Page](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326026/box-application_geqlum.jpg)
    ![Box Application Success Modal](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326025/box-application-success_arrhb7.jpg)
    ![Box Application Already Sent View](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326026/box-application-sent_tyqgx2.jpg)
    ![Mentor's Telegram Notification for New Application](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326037/telegram-box-application_ycwbsw.png)
    ![Student's Telegram Notification of Application Receipt](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326037/telegram-box-application-user_znkty0.png)
    </details>

6.  **Chat with Mentor**
    * A real-time chat interface with support for text messages and image uploads.
    * An efficient "Load Previous" button for message history pagination.
    * Unread message counters in the header and sidebar ensure users never miss a message.
    * **Telegram** notifications for all new messages to ensure instant communication.

    <details>
    <summary>🖼️ View Screenshots</summary>
    
    ![Student Chat Page](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326026/chat_ga0pxy.jpg)
    ![Student's Telegram Notification](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326038/telegram-chat_rd8mud.png)
    ![Mentor's Telegram Notification](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326038/telegram-chat-admin_fnx55e.png)
    </details>

7.  **User Profile**
    * A dedicated page for users to update their personal information (name, phone, email, avatar) and securely change their password.
    
    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Profile Page](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326034/profile_edy6bl.jpg)
    </details>

### III. Custom Admin Panel for Mentor

8.  **Mentor Dashboard**
    * An "at-a-glance" dashboard summarizing the most critical information: pending homework, recent unread messages, and widgets for the highest and lowest student progress.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Mentor Dashboard](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326033/mentor-dashboard_uhe0we.jpg)
    </details>

9.  **Homework Review Workflow**
    * A dedicated section to manage all student submissions with filters for "Pending," "Approved," and "All."
    * A detailed review page where the mentor can view the student's photo and comments, provide feedback, and either "Approve" or "Reject" the work.
    * This action triggers an automated notification to the student via the platform chat and **Telegram**, including the mentor's feedback.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Homework Review List](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326037/tasks-list_qxu0oz.jpg)
    ![Detailed Review Page](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326037/tasks-detail_ehxigr.jpg)
    ![Homework Submission Notification to Admin](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326037/tasks-detail_1_ibkzza.jpg)
    ![Homework Approval Notification to User](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326045/user-telegram-tasks_fhhtst.png)
    ![Homework Rejection Notification to User](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326037/tasks-detail_1_ibkzza.jpg)
    ![Platform Chat Notification after Review](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326045/user-task-review-chat_ehdpry.jpg)
    </details>

10. **Chat Management**
    * A centralized list of all student chats, sorted by recent activity and unread message count.
    * Includes a search filter to quickly find a student by name or email.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Admin Chat List](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326025/admin-all-chats_hdgvwx.jpg)
    </details>

11. **Lecture Management (CRUD)**
    * Full CRUD (Create, Read, Update, Delete) functionality for course lectures.
    * A robust **positional number system** allows the mentor to easily reorder lessons without being dependent on database primary keys.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Lecture List](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326032/lecture-list_qu6o59.jpg)
    ![Edit Lecture](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326032/lecture-list_qu6o59.jpg)
    ![Delete Lecture Confirmation](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326031/lecture-delete_xaaunm.jpg)
    ![Create Lecture](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326031/lecture-create_ubbufw.jpg)
    </details>

12. **Student List**
    * A comprehensive overview of all students, displaying their progress, tier, and last activity.
    * Features two switchable view modes (grid and list) and advanced filters for progress and search queries.

    <details>
    <summary>🖼️ View Screenshots</summary>
    
    ![Student List (Grid View)](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326035/students-list_zvq6e1.jpg)
    ![Student List (List View)](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326036/students-list_1_uaohlo.jpg)
    </details>

13. **Start Box Application Management**
    * A queue for managing starter kit applications with "Pending" and "Sent" filters.
    * A "Mark as Sent" button that automates the notification process to the student.

    <details>
    <summary>🖼️ View Screenshots</summary>

    ![Box Application List](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326025/box-application-list_esixpn.jpg)
    </details>

### IV. Additional Pages & Status Handling

* **Custom Error Pages:** Beautifully designed pages for 404, 500, and other HTTP errors, handled by custom middleware.
* **Payment Status Pages:** Themed pages for successful, canceled, and failed payments to maintain a consistent user experience.

<details>
<summary>🖼️ View Screenshots</summary>

![Success Pay Page](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326036/success_pay_w7n5j3.jpg)
![Cancel Pay Page](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326026/cancel-pay_mc95pu.jpg)
![Error Pay Page](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326026/error_pay_gulohe.jpg)
![404 Page](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326024/404_dweekt.jpg)
![500 Page](https://res.cloudinary.com/dpxuxiswa/image/upload/v1754326025/500_wa3w5h.jpg)
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

To run the tests:
```bash
pytest
```
