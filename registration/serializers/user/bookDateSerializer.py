from django.conf import settings
from rest_framework import serializers
from ...models.evaluation import Reservation, EnglishTest
from django.utils.timezone import datetime, timedelta


class BookDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["id", "gender", "faculty", "reservation_date", "start_time", "duration_time", "online"]


class SetBookEnglishSerializer(serializers.ModelSerializer):
    test_try = serializers.IntegerField()

    class Meta:
        model = EnglishTest
        fields = ("applicant_id", "reservation_id", "test_try",)

    error_msg = {
        "limit": {
            "limit_exceed": "Sorry, you exceed the maximum limit of the test.",
            "limit_exceed_ar": "عذرا ، لقد تجاوزت الحد الأقصى للاختبار."
        },
        "capacity": {
            "date_unavailable": "This Date is Unavailable",
            "date_unavailable_ar": "التاريخ غير متاح"
        },
        "applicantId": {
            "applicant_id": "You alraedy reserved English Test date!",
            "applicant_id_ar": "لقد حجزت بالفعل موعد اختبار اللغة الإنجليزية!"
        },
        "reservation": {
            "reservation": "This date is already full!",
            "reservation_ar": "لقد تم حجز هذا الموعد بالكامل"
        },
        "pending": {
            "pending": "You Already Have a Unconfirmed English Booking",
            "pending_ar": "لديك بالفعل حجز إنجليزي غير مؤكد"
        },
        "payment": {
            "payment": "You Have a pending Payment for English Test",
            "payment_ar": "لديك دفعة معلقة لاختبار اللغة الإنجليزية"
        },
        "semester": {
            "wrong_semester": "Sorry, you can\'t book an english test for this semester, Please register again.",
            "wrong_semester_ar": "عفواً، لا يمكنك حجز اختبار اللغة الانجليزية في هذا الفصل، برجاء التسجيل مرة أخرى."}
    }

    def validate(self, attrs):
        if attrs['applicant_id'].apply_semester != settings.CURRENT_SEMESTER:
            raise serializers.ValidationError(self.error_msg['semester'])
        capacity = attrs['reservation_id'].capacity
        date = attrs['reservation_id'].reservation_date
        time = attrs['reservation_id'].start_time
        count = attrs['reservation_id'].count
        time_now = datetime.now()
        time_due = (timedelta(hours=attrs['reservation_id'].duration_time) + datetime.strptime(str(time),
                                                                                               '%H:%M:%S')).time()
        if capacity == count:
            raise serializers.ValidationError(self.error_msg['reservation'])

        if capacity == 0:
            raise serializers.ValidationError(self.error_msg['capacity'])

        if date == time_now.date() and (time <= time_now.time() or time_due <= time_now.time()):
            raise serializers.ValidationError(self.error_msg['capacity'])

        if EnglishTest.objects.filter(applicant_id=attrs['applicant_id'], paid=False).exists():
            raise serializers.ValidationError(self.error_msg['payment'])
        
        if EnglishTest.objects.filter(applicant_id=attrs['applicant_id'],test_try=3).exists():
            raise serializers.ValidationError(self.error_msg['limit'])
        
        # if EnglishTest.objects.filter(applicant_id=attrs['applicant_id'], paid=True, confirmed=False).exists():
        #     raise serializers.ValidationError(self.error_msg['pending'])

        return attrs

    def create(self, validated_data):
        add = EnglishTest(
            applicant_id=validated_data['applicant_id'],
            reservation_id=validated_data['reservation_id'],
            test_try=validated_data['test_try'] + 1
        )
        if not EnglishTest.objects.filter(applicant_id=validated_data['applicant_id']):
            add.paid = True
        reserve = validated_data['reservation_id']
        reserve.count = reserve.count + 1
        reserve.reserved = True
        reserve.save()
        return add.save()
