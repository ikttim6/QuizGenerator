from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Document
from .forms import DocumentUploadForm
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
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()

            # Extract text from the uploaded file
            extracted_text = extract_text_from_file(document.file.path)
            document.content = extracted_text
            document.save()

            messages.success(request, 'Document uploaded successfully!')
            return redirect('document_list')
    else:
        form = DocumentUploadForm()

    return render(request, 'documents/upload_document.html', {'form': form})


@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk, uploaded_by=request.user)
    return render(request, 'documents/document_detail.html', {'document': document})


@login_required
def delete_document(request, pk):
    document = get_object_or_404(Document, pk=pk, uploaded_by=request.user)

    if request.method == 'POST':
        document.file.delete()
        document.delete()
        messages.success(request, 'Document deleted successfully!')
        return redirect('document_list')

    return render(request, 'documents/delete_document.html', {'document': document})
