# urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (
    upload_pdf,
    pdf_list,
    ask_question,
    convert_pdf_to_speech,
    text_to_speech_view,
    home,
    upload_screenshot_view,
    open_sketchbook,
    sketch_opened,
    capture_frame_view, 
    create_pdf_view,
    photos,quiz_view
   # voice_assistant_view,  # Import the new view
)

urlpatterns = [
    path('upload/', upload_pdf, name='upload_pdf'),
    path('pdfs/', pdf_list, name='pdf_list'),
    path('ask/<int:pdf_id>/', ask_question, name='ask_question'),
    path('convert_pdf_to_speech/<int:pdf_id>/', convert_pdf_to_speech, name='convert_pdf_to_speech'),
    path('text_to_speech/<int:pdf_id>/', text_to_speech_view, name='text_to_speech'),
    #path('voice_assistant/', voice_assistant_view, name='voice_assistant'),  # Add this line
    path('upload_screenshot/', upload_screenshot_view, name='upload_screenshot'),
    path('quiz/<int:pdf_id>/',quiz_view, name='quiz_view'),
    path('', home, name='home'),
    path('open_sketchbook/', open_sketchbook, name='open_sketchbook'),
    path('sketch_opened/', sketch_opened, name='sketch_opened'),
    path('photos/',photos,name='photos'),
    path('capture_frame/', capture_frame_view, name='capture_frame'),
    path('create_pdf/', create_pdf_view, name='create_pdf'),
     path('quiz/<int:pdf_id>/', quiz_view, name='quiz_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
