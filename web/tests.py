from multiprocessing.resource_tracker import register

import pytest
from django.urls import reverse
from django.utils import timezone

from web.models import UserModel, Order, SubscribeTariff, Code


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
def subscribe_tariff_base(db):
    return SubscribeTariff.objects.create(
        name="base",
        price="250",
        with_startbox=False
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
def test_create_checkout_session_creates_order_status_303(db, client, mocker, subscribe_tariff_base):
    mocker_checkout_session = mocker.patch("stripe.checkout.Session.create")
    mocker_checkout_session.return_value = mocker.MagicMock(
        id="cs_test_123",
        url="https://stripe.com/test"
    )
    data = {
        "action": "base"
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
def test_register_user_with_code(db, client, code_master, user):
    data = {
        "first_name": "Dmytro",
        "last_name": "Ukrainets",
        "email": "test@lerner.com",
        "password1": "1qazxsw23edcvfr4-=",
        "password2": "1qazxsw23edcvfr4-=",
        "code": code_master.code,
    }
    response = client.post(reverse("register"), data=data)

    new_user = UserModel.objects.filter(email="test@lerner.com").first()

    assert response.status_code == 302

    assert new_user.first_name == "Dmytro"
    assert new_user.last_name == "Ukrainets"
    assert new_user.code == code_master

    code_master.refresh_from_db()

    assert code_master.activated_date.timestamp() == pytest.approx(timezone.now().timestamp())
    assert code_master.is_activated == True
    assert code_master.start_box_coupon_is_activated == False

