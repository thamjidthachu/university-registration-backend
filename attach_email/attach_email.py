def get_attach_file(type):
    from django.conf import settings
    from django.core.files import File
    import os

    attaches = []
    if type == 'english':
        with open(settings.BASE_DIR / 'attach_email/User Guide for Students - Oxford Test via Zoom.pdf', 'rb') as fileOpen:
            file = File(fileOpen, name=os.path.basename(fileOpen.name))
            attaches.append({
                "name": file.name,
                "file": file.read()
            })
    elif type == "interview":
        with open(settings.BASE_DIR / 'attach_email/دليل المستخدم المقابلة الشخصية من خلال برنامج Zoom للطلبة.pdf',
                  'rb') as fileOpen:
            file = File(fileOpen, name=os.path.basename(fileOpen.name))
            attaches.append({
                "name": file.name,
                "file": file.read()
            })

    elif type == "outside":
        with open(settings.BASE_DIR / "attach_email/student_outside/Student's Guide (النهائي).pdf",
                  'rb') as fileOpen:
            file = File(fileOpen, name=os.path.basename(fileOpen.name))
            attaches.append({
                "name": file.name,
                "file": file.read()
            })

        with open(settings.BASE_DIR / "attach_email/student_outside/الدليل الارشادي للطلبة المستجدين.pdf",
                  'rb') as fileOpen:
            file = File(fileOpen, name=os.path.basename(fileOpen.name))
            attaches.append({
                "name": file.name,
                "file": file.read()
            })

        with open(settings.BASE_DIR / "attach_email/student_outside/إقرار بالانظمة واللوائح.pdf",
                  'rb') as fileOpen:
            file = File(fileOpen, name=os.path.basename(fileOpen.name))
            attaches.append({
                "name": file.name,
                "file": file.read()
            })

        with open(settings.BASE_DIR / "attach_email/student_outside/إقرار بالانظمة واللوائح باللغة الانجليزية.pdf",
                  'rb') as fileOpen:
            file = File(fileOpen, name=os.path.basename(fileOpen.name))
            attaches.append({
                "name": file.name,
                "file": file.read()
            })

    return attaches
