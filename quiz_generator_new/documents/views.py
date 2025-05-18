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
                # Write the uploaded file to the /tmp directory
                with open(temp_file_path, 'wb+') as destination:
                    for chunk in uploaded_file_obj.chunks():
                        destination.write(chunk)
                
                # Now, extract text from the file stored in /tmp
                extracted_text = extract_text_from_file(temp_file_path)
                processed_successfully = True

            except Exception as e:
                # Log the exception e for debugging (e.g., print(f"Error: {e}") or proper logging)
                print(f"Error during file processing: {e}") 
                messages.error(request, f"An error occurred while processing the file: {str(e)}")
            finally:
                # Always try to clean up the temporary file
                if os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                        print(f"Temporary file '{temp_file_path}' deleted.")
                    except OSError as e_remove:
                        # Log this error, but don't necessarily fail the request
                        print(f"Error removing temporary file {temp_file_path}: {e_remove}")

            if processed_successfully:
                # Create the Document model instance.
                # We are NOT using form.save() directly here to have more control
                # over the 'file' field and prevent Django's default storage
                # from trying to save the file to the read-only MEDIA_ROOT.
                
                document = Document(
                    title=form.cleaned_data['title'],
                    uploaded_by=request.user,
                    content=extracted_text
                )
                
                # We explicitly set the 'name' attribute of the FileField.
                # Given your model's `upload_to='documents/'`, Django will store
                # 'documents/original_filename.ext' (or just 'original_filename.ext'
                # if original_filename already includes 'documents/') in the database.
                # No actual file content is written by Django's storage system here.
                document.file.name = original_filename 
                
                document.save() # Save the model instance with metadata and filename

                messages.success(request, 'Document uploaded and content extracted successfully!')
                return redirect('document_list')
            else:
                # If processing failed, an error message should have been set.
                # Re-render the form to show errors or allow re-upload.
                return render(request, 'documents/upload_document.html', {'form': form})
        else:
            # Form is not valid, re-render with form errors
            return render(request, 'documents/upload_document.html', {'form': form})
    else:
        form = DocumentUploadForm()
    return render(request, 'documents/upload_document.html', {'form': form})


@login_required
def document_detail(request, pk):
    # This view should be fine as it primarily reads from the database.
    # document.file.url or document.file.path would not point to an accessible file
    # if you tried to use them to serve the file, but you're not doing that here.
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
        # Since we are not using Django's file storage to save the actual file persistently,
        # document.file.delete() is unnecessary and could potentially cause issues
        # if it tries to delete a file from a location it doesn't manage or that doesn't exist.
        # The file in /tmp is already gone or will be cleaned up by the OS.
        # The database record for the file (the filename string) will be removed
        # when document.delete() is called.
        
        # REMOVED: document.file.delete()

        document.delete() # This deletes the model instance from the database
        messages.success(request, 'Document metadata deleted successfully!') # Clarified message
        return redirect('document_list')

    return render(request, 'documents/delete_document.html', {'document': document})