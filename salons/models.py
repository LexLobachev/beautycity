from django.db import models
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField


class Salon(models.Model):
    name = models.CharField("название",  max_length=200)
    city = models.CharField("город", max_length=50, default="Москва")
    address = models.CharField("адрес", max_length=200)
    latitude = models.DecimalField("широта", max_digits=6, decimal_places=3)
    longitude = models.DecimalField("долгота", max_digits=6, decimal_places=3)

    def __str__(self):
        return f'Салон {self.name}'


class Provider(models.Model):
    first_name = models.CharField("имя", max_length=50)
    last_name = models.CharField("фамилия", max_length=50)
    photo = models.ImageField("фото", upload_to='providers',
                              null=True, blank=True)
    works_at = models.ManyToManyField(Salon, verbose_name="где работает",
                                      related_name='providers', related_query_name='provider',
                                      through='ProviderSchedule')

    def __str__(self):
        return f'Мастер {self.first_name} {self.last_name}'


class ProviderSchedule(models.Model):
    WEEKDAYS = [
        (0, _("Monday")),
        (1, _("Tuesday")),
        (2, _("Wednesday")),
        (3, _("Thursday")),
        (4, _("Friday")),
        (5, _("Saturday")),
        (6, _("Sunday")),
    ]
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE,
                                 verbose_name="мастер",
                                 related_name='working_timeslots')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE,
                              verbose_name="салон",
                              related_name='provider_schedules')
    weekday = models.IntegerField("день недели", choices=WEEKDAYS)
    from_hour = models.TimeField("начало работы",
                                 help_text=_('Only exact hours with 00 minutes are allowed, '
                                             'e.g. 11:00, 14:00'))
    to_hour = models.TimeField("конец работы",
                               help_text=_('Only exact hours with 00 minutes are allowed, '
                                           'e.g. 11:00, 14:00'))

    # TODO better unique constraint - work in multiple salons on the same day, have breaks
    class Meta:
        unique_together = ['provider', 'weekday']

    def __str__(self):
        return f'{self.provider} c {self.from_hour} по {self.to_hour} в {self.get_weekday_display()}'


class Service(models.Model):
    name = models.CharField("название",  max_length=200)
    price = models.DecimalField("цена", max_digits=8, decimal_places=2)
    provided_by = models.ManyToManyField(Provider, verbose_name="предоставляют мастера",
                                         related_name='services', related_query_name='service')

    def __str__(self):
        return f'Услуга {self.name}'


class Customer(models.Model):
    telegram_id = models.IntegerField()
    first_name = models.CharField("имя", max_length=50)
    last_name = models.CharField("фамилия", max_length=50)
    phone_number = PhoneNumberField("телефон")

    def __str__(self):
        return f'Клиент {self.first_name} {self.last_name}'


class Appointment(models.Model):
    date = models.DateField("дата")
    time = models.TimeField("время")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                 verbose_name="клиент",
                                 related_name='appointments')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE,
                                 verbose_name="мастер",
                                 related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE,
                                verbose_name="услуга")

    class Meta:
        unique_together = ['provider', 'date', 'time']

    @property
    def salon(self):
        matching_schedule = ProviderSchedule.objects.get(
            provider=self.provider,
            weekday=self.date.weekday(),
            from_hour__lte=self.time,
            to_hour__gt=self.time,
        )
        return matching_schedule.salon

    def __str__(self):
        return f'Запись {self.customer} к {self.provider} в {self.salon}, {self.date} {self.time}'
