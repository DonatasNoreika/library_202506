from django.db import models
import uuid
from django.contrib.auth.models import User
from datetime import date
from tinymce.models import HTMLField
from PIL import Image


# Create your models here.
class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(verbose_name="Vardas", max_length=100)
    last_name = models.CharField(verbose_name="Pavardė", max_length=100)
    description = HTMLField(verbose_name="Aprašymas", max_length=3000, default="")

    def display_books(self):
        return ", ".join(book.title for book in self.books.all())

    display_books.short_description = "Knygos"

    class Meta:
        verbose_name = "Autorius"
        verbose_name_plural = "Autoriai"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    title = models.CharField(verbose_name="Pavadinimas", max_length=200)
    summary = models.TextField(verbose_name="Aprašymas", max_length=1000, help_text='Trumpas knygos aprašymas')
    isbn = models.CharField(verbose_name="ISBN", max_length=13,
                            help_text='13 Simbolių <a href="https://www.isbn-international.org/content/what-isbn">ISBN kodas</a>')
    cover = models.ImageField(verbose_name="Viršelis", upload_to='covers', null=True, blank=True)
    author = models.ForeignKey(to="Author", verbose_name="Autorius", on_delete=models.SET_NULL, null=True, blank=True, related_name="books")
    genre = models.ManyToManyField(to="Genre", verbose_name="Žanras", help_text='Išrinkite žanrą(us) šiai knygai')

    # def display_genre(self):
    #     genres = self.genre.all()
    #     result = ""
    #     for genre in genres:
    #         result += genre.name + ", "
    #     return result

    def display_genre(self):
        return ', '.join(genre.name for genre in self.genre.all())

    display_genre.short_description = "Žanras"

    class Meta:
        verbose_name = "Knyga"
        verbose_name_plural = "Knygos"

    def __str__(self):
        return f"{self.title} ({self.author})"


class Genre(models.Model):
    name = models.CharField(verbose_name="Pavadinimas", max_length=200,
                            help_text='Įveskite knygos žanrą (pvz. detektyvas)')

    class Meta:
        verbose_name = "Žanras"
        verbose_name_plural = "Žanrai"

    def __str__(self):
        return self.name


class BookInstance(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, help_text='Unikalus ID knygos kopijai')
    due_back = models.DateField(verbose_name="Bus prieinama", null=True, blank=True)
    book = models.ForeignKey(to="Book", verbose_name="Knyga", on_delete=models.SET_NULL, null=True, blank=True, related_name="instances")
    reader = models.ForeignKey(to=User, verbose_name="Skaitytojas", on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ('a', 'Administruojama'),
        ('p', 'Paimta'),
        ('g', 'Galima paimti'),
        ('r', 'Rezervuota'),
    )

    status = models.CharField(verbose_name="Būsena", max_length=1, choices=LOAN_STATUS, blank=True, default="a")

    def is_overdue(self):
        return self.due_back and self.due_back < date.today()


    class Meta:
        verbose_name = "Kopija"
        verbose_name_plural = "Kopijos"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.book} ({self.uuid})"


class BookReview(models.Model):
    book = models.ForeignKey(to="Book", verbose_name="Knyga", on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    reviewer = models.ForeignKey(to=User, verbose_name="Komentatorius", on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateTimeField(verbose_name="Data", auto_now_add=True)
    content = models.TextField(verbose_name="Atsiliepimas", max_length=2000)

    class Meta:
        verbose_name = "Atsiliepimas"
        verbose_name_plural = 'Atsiliepimai'
        ordering = ['-date_created']


class Profile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    photo = models.ImageField(verbose_name="Nuotrauka", upload_to="profile_pics", default="profile_pics/default.png")

    class Meta:
        verbose_name = "Profilis"
        verbose_name_plural = 'Profiliai'

    def __str__(self):
        return f"{self.user.username} profilis"

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(*args, force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)
        img = Image.open(self.photo.path)
        if img.height > 300 or img.width > 300:
            img.thumbnail((300, 300))
            img.save(self.photo.path)