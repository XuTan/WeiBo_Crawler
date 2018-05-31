# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.urls import reverse


class Keywords(models.Model):
    keyword = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'keywords'
        unique_together = (('id', 'keyword'),)

    def __str__(self):  # note the string return is necessary
        return self.keyword


class Userdata(models.Model):
    id = models.BigAutoField(primary_key=True)
    uid = models.CharField(max_length=40)
    keyword = models.CharField(max_length=40)
    user_screen_name = models.CharField(max_length=40)
    user_main_page = models.CharField(max_length=40)
    user_desc1 = models.TextField()
    user_desc2_fans = models.CharField(max_length=40)
    user_image_url = models.TextField()

    class Meta:
        managed = False
        db_table = 'userdata'
        unique_together = (('id', 'uid'),)

    def __str__(self):
        return self.user_screen_name


class Weibodata(models.Model):
    id = models.BigAutoField(primary_key=True)
    uid = models.CharField(max_length=40)
    weibo_screen_name = models.CharField(max_length=40)
    weibo_scheme = models.TextField()
    weibo_created_at = models.DateField()
    keyword = models.CharField(max_length=40)
    weibo_text = models.TextField()
    weibo_raw_text = models.TextField()
    weibo_comments_count = models.CharField(max_length=40)
    weibo_attitudes_count = models.CharField(max_length=40)
    weibo_reposts_count = models.CharField(max_length=40)
    weibo_pics1 = models.TextField(blank=True, null=True)
    weibo_pics2 = models.TextField(blank=True, null=True)
    weibo_pics3 = models.TextField(blank=True, null=True)
    weibo_pics4 = models.TextField(blank=True, null=True)
    weibo_pics5 = models.TextField(blank=True, null=True)
    weibo_pics6 = models.TextField(blank=True, null=True)
    weibo_pics7 = models.TextField(blank=True, null=True)
    weibo_pics8 = models.TextField(blank=True, null=True)
    weibo_pics9 = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'weibodata'
        unique_together = (('id', 'weibo_raw_text'),)
        ordering = ['-weibo_created_at']

    def get_absolute_url(self):
        return reverse('weibo:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.weibo_raw_text
