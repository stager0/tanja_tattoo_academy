import pytest
from django.urls import reverse

from web.models import UserModel, Order, SubscribeTariff


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
def subscribe_tariff_base(db):
    return SubscribeTariff.objects.create(
        name="base",
        price="250",
        with_startbox=False
    )


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


