import pytest
from django.urls import reverse
from pytest_mock import mocker

from web.models import UserModel


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


# Create your tests here.
