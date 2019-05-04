from django.db import models

class Book(models.Model):
    isbn = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    book_location = models.CharField(max_length=50)
    update_date = models.DateTimeField()
    nfc_id_fk = models.IntegerField(blank=True, null=True)
    image_source = models.CharField(max_length=255, blank=True, null=True)
    company_fk = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'book_tb'


class Company(models.Model):
    register_id = models.AutoField(primary_key=True)
    company_nm = models.CharField(unique=True, max_length=100)
    service_nm = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'company_tb'

class Isbn(models.Model):
    isbn = models.CharField(max_length=20)
    book_nm = models.CharField(max_length=200, blank=True, null=True)
    author = models.CharField(max_length=80)
    keyword = models.CharField(max_length=255, blank=True, null=True)
    publish_year = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'isbn_tb'


class LibraryOpiton(models.Model):
    option_name = models.CharField(max_length=255, blank=True, null=True)
    search_option = models.CharField(max_length=100, blank=True, null=True)
    company_fk = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'library_opiton_tb'


class Nfc(models.Model):
    id = models.IntegerField(primary_key=True)
    shelf_height = models.IntegerField()
    shelf_location = models.CharField(max_length=100)
    image_source = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nfc_tb'


class Qna(models.Model):
    userkey_fk = models.CharField(max_length=50, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    content = models.CharField(max_length=255, blank=True, null=True)
    managerkey_fk = models.IntegerField(blank=True, null=True)
    answer = models.CharField(max_length=255, blank=True, null=True)
    answerdate = models.DateTimeField(blank=True, null=True)
    library_fk = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'qna_tb'


class User(models.Model):
    userkey_id = models.CharField(primary_key=True, max_length=50)
    library = models.IntegerField()
    user_status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user_tb'