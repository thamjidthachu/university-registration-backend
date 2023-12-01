from django.conf import settings
from rest_framework import serializers
from registration.models.applicant import Reservation
from registration.models.evaluation import Interview
from django.utils.timezone import datetime, timedelta


# Implemented By Mohamed Samy.

class InterviewBookSerializer(serializers.ModelSerializer):
    """
        This class for handle the serializer data that coming as a json data
        - should be handle each field that coming as a json.
        - validate each field
        - store the data after validate into database or
        - return validate error if have an error
    """

    # handle expected errors
    error_msg = {
        'applicantId': {'applicant_id': "You already reserved Interview date!",
                        "applicant_id_ar": "لقد حجزت بالفعل موعد المقابلة!"},
        'capacity': {'capacity': 'This time slot is no longer can be Reserved',
                     "capacity_ar": "لم يعد من الممكن حجز هذه الفترة الزمنية"},
        "reservation": {"reservation": "This date is already full!",
                        "reservation_ar": "لقد تم حجز هذا الموعد بالكامل"},
        "interview": {
            "interview": "you have already book date for interview",
            "interview_ar": "لديك بالفعل تاريخ الكتاب للمقابلة",
        },
        "semester": {"wrong_semester": "Sorry, you can\'t book an interview for this semester, Please register again.",
                     "wrong_semester_ar": "عفواً، لا يمكنك حجز المقابلة الشخصية في هذا الفصل، برجاء التسجيل مرة أخرى."}
    }

    # Should be add model class
    # fields that need to validate it
    class Meta:
        model = Interview
        fields = ("applicant_id", 'reservation_id',)

    # this function use for validate the data
    # return data if success validate or return errors if have an error
    def validate(self, validate_data):
        if validate_data['applicant_id'].apply_semester != settings.CURRENT_SEMESTER:
            raise serializers.ValidationError(self.error_msg['semester'])

        applicant = Interview.objects.filter(applicant_id=validate_data['applicant_id'].id)

        if applicant.exists():
            raise serializers.ValidationError(self.error_msg['applicantId'])

        capacity = validate_data['reservation_id'].capacity
        date = validate_data['reservation_id'].reservation_date
        time = validate_data['reservation_id'].start_time
        count = validate_data['reservation_id'].count
        interview = Interview.objects.filter(applicant_id=validate_data['applicant_id'],
                                             applicant_id__apply_semester=settings.CURRENT_SEMESTER).exists()
        time_now = datetime.now()
        time_due = (timedelta(hours=validate_data['reservation_id'].duration_time)
                    + datetime.strptime(str(time), '%H:%M:%S')).time()

        if capacity == count:
            raise serializers.ValidationError(self.error_msg['reservation'])

        if capacity == 0:
            raise serializers.ValidationError(self.error_msg['reservationId'])

        if date == time_now.date() and (time <= time_now.time() or time_due <= time_now.time()):
            raise serializers.ValidationError(self.error_msg['capacity'])

        if interview:
            raise serializers.ValidationError(self.error_msg['interview'])

        return validate_data

    # this function is called after success validation
    # it use for save data into the database
    def create(self, validated_data):

        reserved = Interview(
            applicant_id=validated_data.get('applicant_id'),
            reservation_id=validated_data.get('reservation_id'),
        )
        reserved.save()
        return reserved

    def update(self, instance, validated_data=None):

        instance.count = instance.count + 1
        instance.reserved = True
        instance.save()

        return instance


class InterviewBookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ("id", "reservation_date", "start_time",)
