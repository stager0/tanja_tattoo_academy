import pytest
from django.urls import reverse
from django.utils import timezone

from web.models import UserModel, Order, SubscribeTariff, Code, Chat, ResetCode


@pytest.fixture
def admin_user(db):
    admin = UserModel.objects.create_superuser(
        first_name="Bella",
        last_name="Admin",
        telegram_chat_id="1111111111",
        email="admin@admin.com"
    )
    admin.set_password("1qaz")
    return admin

@pytest.fixture
def user(db):
    user = UserModel.objects.create_user(
        first_name="Antonino",
        last_name="Bombardino",
        telegram_chat_id="2222222222",
        email="user@user.com"
    )
    user.set_password("1qaz")
    return user

@pytest.fixture
def user_without_chat(db):
    user = UserModel.objects.create_user(
        first_name="Larisa",
        last_name="Muller",
        email="larisa@user.com"
    )
    user.set_password("1qaz")
    return user

@pytest.fixture
def subscribe_tariff_base(db):
    return SubscribeTariff.objects.create(
        name="base",
        price="250",
        with_startbox=False
    )

@pytest.fixture
def subscribe_tariff_pro(db):
    return SubscribeTariff.objects.create(
        name="pro",
        price="500",
        with_startbox=True
    )

@pytest.fixture
def subscribe_tariff_master(db):
    return SubscribeTariff.objects.create(
        name="master",
        price="750",
        with_startbox=True
    )

@pytest.fixture
def order(db, subscribe_tariff_base):
    price = SubscribeTariff.objects.get(name="base").price
    return Order.objects.create(total_sum=price)

@pytest.fixture
def order_paid_master(db, subscribe_tariff_master, user):
    return Order.objects.create(
        total_sum=subscribe_tariff_master.price,
        is_paid=True,
        user_email=user.email,
        session_id="361253762154"
    )

@pytest.fixture
def code_master(db, order_paid_master):
    return Code.objects.create(
        code="ASDF-ASDF-ASDF",
        order=order_paid_master,
        tariff="master"
    )

# -------------------------TESTS---------------------------

@pytest.mark.django_db
def test_send_index_form_valid_status_302(client, admin_user, mocker):
    url = reverse("index")
    data = {
        "name": "Antonino Bombardino",
        "contact_method": "Telegram",
        "contact_details": "No details",
        "action": "submit"
    }
    mock_telegram = mocker.patch("web.views.send_message_in_telegram")
    mock_telegram.return_value.status_code = 200
    response = client.post(url, data=data)

    assert response.status_code == 302
    assert "answer_to_form/" in response.url
    mock_telegram.assert_called_once()


@pytest.mark.django_db
def test_send_index_invalid_form_status_400(client):
    url = reverse("index")
    invalid_data = {"name": "not all data", "action": "submit"}
    response = client.post(url, data=invalid_data)
    assert response.status_code == 400

@pytest.mark.django_db
@pytest.mark.parametrize("action", ["base", "pro", "master"])
def test_create_checkout_session_creates_order_status_303(db, client, mocker, subscribe_tariff_base, subscribe_tariff_pro, subscribe_tariff_master, action):
    mocker_checkout_session = mocker.patch("stripe.checkout.Session.create")
    mocker_checkout_session.return_value = mocker.MagicMock(
        id="cs_test_123",
        url="https://stripe.com/test"
    )
    data = {
        "action": action
    }
    orders_count_before = Order.objects.count()
    response = client.post(reverse("checkout_session"), data=data)
    orders_count_after = Order.objects.count()

    assert orders_count_after == orders_count_before + 1
    assert response.url == "https://stripe.com/test"
    assert response.status_code == 303
    mocker_checkout_session.assert_called_once()


@pytest.mark.django_db
def test_stripe_webhook_changes_order_and_creates_new_code_also_sends_email(db, mocker, admin_user, client, order, subscribe_tariff_base):
    mocker_webhook = mocker.patch("stripe.Webhook.construct_event")
    session_id = "1212"
    mocker_webhook.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": session_id,
                "customer_details": {
                    "email": admin_user.email,
                    "name": admin_user.get_full_name()
                },
                "metadata": {
                    "order_id": order.pk,
                    "tariff": subscribe_tariff_base.name,
                }
            }
        }
    }
    mocker_mailjet = mocker.patch("web.views.send_email_subscribe_code")
    mocker_mailjet.return_value = None

    response = client.post(reverse("webhook"))
    order.refresh_from_db()

    new_code = Code.objects.first()

    assert response.status_code == 200
    assert order.is_paid == True
    assert order.user_email == admin_user.email
    assert order.session_id == session_id
    assert new_code.order == order
    assert new_code.tariff == subscribe_tariff_base.name
    mocker_mailjet.assert_called_once()


@pytest.mark.django_db
def test_register_user_with_code(db, client, mocker, code_master, user, admin_user):
    mocker_mailjet = mocker.patch("web.views.send_after_register_email")
    mocker_mailjet.return_value.status_code = 200
    mocker_notification = mocker.patch("web.views.send_message_in_telegram")
    mocker_notification.return_value.status_code = 200
    data = {
        "first_name": "Dmytro",
        "last_name": "Ukrainets",
        "email": "test@lerner.com",
        "password1": "1qazxsw23edcvfr4-=",
        "password2": "1qazxsw23edcvfr4-=",
        "code": code_master.code,
    }
    response = client.post(reverse("register"), data=data)
    print(response)

    new_user = UserModel.objects.filter(email="test@lerner.com").first()

    assert response.status_code == 302
    assert response.url == reverse("login")

    assert new_user.first_name == "Dmytro"
    assert new_user.last_name == "Ukrainets"
    assert new_user.code == code_master

    code_master.refresh_from_db()

    assert code_master.activated_date.timestamp() == pytest.approx(timezone.now().timestamp())
    assert code_master.is_activated == True
    assert code_master.start_box_coupon_is_activated == False

    new_user_chat_was_created = Chat.objects.filter(user=new_user).exists()

    assert new_user_chat_was_created == True
    mocker_mailjet.assert_called_once()
    mocker_notification.assert_called_once()


@pytest.mark.django_db
def test_change_password_request_200(db, client, mocker, user, user_without_chat):
    mocker_send_password_change_email = mocker.patch("web.views.send_password_change_email")
    mocker_send_password_change_email.return_value.status_code = 200
    mocker_send_message_in_telegram = mocker.patch("web.views.send_message_in_telegram")
    mocker_send_message_in_telegram.return_value.status_code = 200
    mocker_generate_reset_password_code = mocker.patch("web.views.generate_reset_password_code")
    mocker_generate_reset_password_code.return_value = "AAAA-AAAA-AAAA"

    url = reverse("change_password_request")
    request_correct = client.post(url, data={"email": user.email})
    request_not_correct = client.post(url, data={"email": "falsh_email@gmail.com"})
    request_with_user_without_chat = client.post(url, data={"email": user_without_chat.email})
    new_reset_code = ResetCode.objects.all()

    assert request_correct.status_code == 302
    assert request_not_correct.status_code == 302
    assert request_with_user_without_chat.status_code == 302
    assert mocker_send_password_change_email.call_count == 2
    assert mocker_generate_reset_password_code.call_count == 2
    assert new_reset_code.count() == 2
    assert new_reset_code.first().user_email == user.email
    assert new_reset_code.first().code == "AAAA-AAAA-AAAA"


@pytest.mark.django_db
def test_change_password_view_302(db, client, user, code_reset_user_with_chat, user_without_chat, mocker):
    url = reverse("change_password")
    data = {
        "code": code_reset_user_with_chat.code,
        "password1": "qejejejj39123-=",
        "password2": "qejejejj39123-="
    }
    mocker_send_message_in_telegram = mocker.patch("web.views.send_message_in_telegram")
    mocker_send_message_in_telegram.return_value.status_code = 200

    user.refresh_from_db()
    user_password_before = user.password

    response_existing_user = client.post(url, data=data)

    assert code_reset_user_with_chat.is_activated == False
    code_reset_user_with_chat.refresh_from_db()
    assert code_reset_user_with_chat.is_activated == True
    code_reset_user_with_chat.refresh_from_db()
    user.refresh_from_db()
    user_password_after = user.password
    response_activated_code = client.post(url, data=data)
    assert "На жаль, ваш код вже активований." in response_activated_code.content.decode()

    code_reset_user_with_chat.is_activated = False
    code_reset_user_with_chat.created_date = timezone.now() - timedelta(minutes=16)
    code_reset_user_with_chat.save()
    response_expired_date = client.post(url, data=data)
    assert "На жаль, ваш код прострочений." in response_expired_date.content.decode()

    code_reset_user_with_chat.created_date = timezone.now() + timedelta(minutes=15)
    code_reset_user_with_chat.save()
    data["code"] = "INVALD"
    response_invalid_code = client.post(url, data=data)

    assert "Введений код недійсний або пов'язаний з ним акаунт не знайдено." in html.unescape(response_invalid_code.content.decode())

    data["code"] = code_reset_user_with_chat.code
    data["password1"] = "29e7y78qw6129yqhdiwqhid"
    response_different_passwords = client.post(url, data=data)
    form = response_different_passwords.context["form"]
    assert "Паролі не співпадають." in form.non_field_errors()

    assert response_existing_user.status_code == 302
    assert user_password_before != user_password_after
    mocker_send_message_in_telegram.assert_called_once()



