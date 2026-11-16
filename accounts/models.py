from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower


class User(AbstractUser):
    class Role(models.TextChoices):
        MEMBER = "member", "Member"
        ADMIN = "admin", "Admin"

    email = models.EmailField(max_length=254)
    display_name = models.CharField(max_length=60)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("email"), name="unique_email_ci"),
            models.CheckConstraint(
                condition=models.Q(role__in=["member", "admin"]),
                name="valid_role",
            ),
        ]

    def __str__(self):
        return self.username