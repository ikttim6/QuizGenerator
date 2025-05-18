import os  # <<< Add this import
import uuid # <<< Add this import
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Document
from .forms import DocumentUploadForm # Assuming this is a ModelForm for Document
from .utils import extract_text_from_file


@login_required
def document_list(request):
    documents = Document.objects.filter(uploaded_by=request.user)
    return render(request, 'documents/document_list.html', {'documents': documents})


@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the uploaded file object from the form's cleaned_data
            # This is an InMemoryUploadedFile or TemporaryUploadedFile
            uploaded_file_obj = form.cleaned_data['file'] # Or request.FILES['file'] if form is not ModelForm
            original_filename = uploaded_file_obj.name

            # Define a path in the /tmp directory
            # Using a unique name to avoid potential collisions.
            unique_temp_filename = f"{uuid.uuid4()}_{original_filename}"
            temp_file_path = os.path.join('/tmp', unique_temp_filename)
            
            extracted_text = ""
            processed_successfully = False

            try:
                with open(temp_file_path, 'wb+') as destination:
                    for chunk in uploaded_file_obj.chunks():
                        destination.write(chunk)
                
                extracted_text = extract_text_from_file(temp_file_path)
                processed_successfully = True

            except Exception as e:
                print(f"Error during file processing: {e}") 
                messages.error(request, f"An error occurred while processing the file: {str(e)}")
            finally:
                if os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                        print(f"Temporary file '{temp_file_path}' deleted.")
                    except OSError as e_remove:

                        print(f"Error removing temporary file {temp_file_path}: {e_remove}")

            if processed_successfully:
                document = Document(
                    title=form.cleaned_data['title'],
                    uploaded_by=request.user,
                    content=extracted_text
                )
                
                document.file.name = original_filename 
                
                document.save() 

                messages.success(request, 'Document uploaded and content extracted successfully!')
                return redirect('document_list')
            else:
                return render(request, 'documents/upload_document.html', {'form': form})
        else:
            return render(request, 'documents/upload_document.html', {'form': form})
    else:
        form = DocumentUploadForm()
    return render(request, 'documents/upload_document.html', {'form': form})


@login_required
def document_detail(request, pk):
    if request.user.is_superuser:
        document = get_object_or_404(Document, pk=pk)
    else:
        document = get_object_or_404(Document, pk=pk, uploaded_by=request.user)
    return render(request, 'documents/document_detail.html', {'document': document})


@login_required
def delete_document(request, pk):
    if request.user.is_superuser:
        document = get_object_or_404(Document, pk=pk)
    else:
        document = get_object_or_404(Document, pk=pk, uploaded_by=request.user)

    if request.method == 'POST':
        messages.success(request, 'Document metadata deleted successfully!')
        return redirect('document_list')

    return render(request, 'documents/delete_document.html', {'document': document})